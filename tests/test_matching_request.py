import json

from tornado.testing import gen_test

from tests.server import TestServer


class TestMatchingRequest(TestServer):
    def _test_error(self, response):
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 1)
        self.assertFalse(response['matching']['ok'])

    def test_not_joined(self):
        self._test_error(self._request({'matching': None}))

    @gen_test
    def test_empty(self):
        connection1 = yield self._connect()

        connection1.write_message(json.dumps({'join': {'self': 1, 'other': [2]}}))
        yield connection1.read_message()

        connection1.write_message(json.dumps({'matching': None}))
        response = yield connection1.read_message()
        self.assertEqual(json.loads(response), {'matching': {'ok': True, 'list': []}})

        connection2 = yield self._connect()
        connection2.write_message(json.dumps({'join': {'self': 1, 'other': [1]}}))

        connection3 = yield self._connect()
        connection3.write_message(json.dumps({'join': {'self': 2, 'other': [2]}}))

        connection1.write_message(json.dumps({'matching': None}))
        response = yield connection1.read_message()
        self.assertEqual(json.loads(response), {'matching': {'ok': True, 'list': []}})

        connection1.close()
        connection2.close()
        connection3.close()

    @gen_test
    def test_not_empty(self):
        connection1 = yield self._connect()

        connection1.write_message(json.dumps({'join': {'self': 1, 'other': [1, 2]}}))
        yield connection1.read_message()

        connection2 = yield self._connect()
        connection2.write_message(json.dumps({'join': {'self': 1, 'other': [1]}}))
        yield connection2.read_message()

        connection1.write_message(json.dumps({'matching': None}))
        response = yield connection1.read_message()
        matching = json.loads(response)['matching']['list']
        self.assertEqual(len(matching), 1)

        connection3 = yield self._connect()
        connection3.write_message(json.dumps({'join': {'self': 2, 'other': [1]}}))
        yield connection3.read_message()

        connection1.write_message(json.dumps({'matching': None}))
        response = yield connection1.read_message()
        matching = json.loads(response)['matching']['list']
        self.assertEqual(len(matching), 2)
        self.assertNotEqual(matching[0], matching[1])

        connection1.close()
        connection2.close()
        connection3.close()
