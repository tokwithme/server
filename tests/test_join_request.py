import json

from tornado.testing import gen_test

from tests.server import TestServer


class TestJoinRequest(TestServer):
    def _test_error(self, response):
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 1)
        self.assertFalse(response['join']['ok'])

    def _test_ok(self, response):
        self.assertTrue(response['join']['ok'])
        self.assertEqual(len(response['join']['id']), 24)

    def test_incorrect_body(self):
        self._test_error(self._request({'join': ''}))
        self._test_error(self._request({'join': 'test'}))
        self._test_error(self._request({'join': []}))
        self._test_error(self._request({'join': True}))
        self._test_error(self._request({'join': 1}))
        self._test_error(self._request({'join': None}))

    def test_incorrect_self(self):
        self._test_error(self._request({'join': {'self': '', 'other': [1]}}))
        self._test_error(self._request({'join': {'self': 'test', 'other': [1]}}))
        self._test_error(self._request({'join': {'self': [], 'other': [1]}}))
        self._test_error(self._request({'join': {'self': 0, 'other': [1]}}))
        self._test_error(self._request({'join': {'self': 3, 'other': [1]}}))
        self._test_error(self._request({'join': {'self': None, 'other': [1]}}))

    def test_incorrect_other(self):
        self._test_error(self._request({'join': {'self': 1, 'other': ''}}))
        self._test_error(self._request({'join': {'self': 1, 'other': 'test'}}))
        self._test_error(self._request({'join': {'self': 1, 'other': []}}))
        self._test_error(self._request({'join': {'self': 1, 'other': [2, 3]}}))
        self._test_error(self._request({'join': {'self': 1, 'other': [1, 2, 1]}}))
        self._test_error(self._request({'join': {'self': 1, 'other': 1}}))
        self._test_error(self._request({'join': {'self': 1, 'other': None}}))

    @gen_test
    def test_already_joined(self):
        connection = yield self._connect()

        connection.write_message(json.dumps({'join': {'self': 1, 'other': [1, 2]}}))
        response = yield connection.read_message()
        self._test_ok(json.loads(response))

        connection.write_message(json.dumps({'join': {'self': 1, 'other': [1, 2]}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response))

        connection.close()

    @gen_test
    def test_join_after_leave(self):
        connection = yield self._connect()

        connection.write_message(json.dumps({'join': {'self': 1, 'other': [1, 2]}}))
        response = yield connection.read_message()
        self._test_ok(json.loads(response))

        connection.write_message(json.dumps({'leave': None}))
        response = yield connection.read_message()
        self.assertEqual({'leave': {'ok': True}}, json.loads(response))

        connection.write_message(json.dumps({'join': {'self': 1, 'other': [1, 2]}}))
        response = yield connection.read_message()
        self._test_ok(json.loads(response))

        connection.close()
