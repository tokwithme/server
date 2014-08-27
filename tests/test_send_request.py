import json

from bson import ObjectId
from tornado.testing import gen_test

from tests.server import TestServer


class TestSendRequest(TestServer):
    def _test_error(self, response, target_id=''):
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 1)
        self.assertFalse(response['send']['ok'])
        self.assertEqual(response['send']['id'], target_id)

    def _test_ok(self, response, target_id):
        self.assertTrue(response['send']['ok'])
        self.assertEqual(response['send']['id'], target_id)

    def test_not_joined(self):
        target_id = str(ObjectId())
        self._test_error(self._request({'send': {'id': target_id, 'data': 'test'}}), target_id)

    def test_incorrect_body(self):
        self._test_error(self._request({'send': ''}))
        self._test_error(self._request({'send': 'test'}))
        self._test_error(self._request({'send': []}))
        self._test_error(self._request({'send': True}))
        self._test_error(self._request({'send': 1}))
        self._test_error(self._request({'send': None}))

    @gen_test
    def test_incorrect_id(self):
        connection = yield self._connect()

        connection.write_message(json.dumps({'join': {'self': 1, 'other': [2]}}))
        yield connection.read_message()

        connection.write_message(json.dumps({'send': {'id': '', 'data': 'test'}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response))

        connection.write_message(json.dumps({'send': {'id': 'test', 'data': 'test'}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response))

        connection.write_message(json.dumps({'send': {'id': [], 'data': 'test'}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response))

        connection.write_message(json.dumps({'send': {'id': {}, 'data': 'test'}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response))

        connection.write_message(json.dumps({'send': {'id': True, 'data': 'test'}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response))

        connection.write_message(json.dumps({'send': {'id': 1, 'data': 'test'}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response))

        connection.write_message(json.dumps({'send': {'id': None, 'data': 'test'}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response))

        connection.close()

    @gen_test
    def test_incorrect_data(self):
        connection = yield self._connect()

        connection.write_message(json.dumps({'join': {'self': 1, 'other': [2]}}))
        yield connection.read_message()

        target_id = str(ObjectId())

        connection.write_message(json.dumps({'send': {'id': target_id, 'data': ''}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response), target_id)

        connection.write_message(json.dumps({'send': {'id': target_id, 'data': []}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response), target_id)

        connection.write_message(json.dumps({'send': {'id': target_id, 'data': {}}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response), target_id)

        connection.write_message(json.dumps({'send': {'id': target_id, 'data': True}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response), target_id)

        connection.write_message(json.dumps({'send': {'id': target_id, 'data': 1}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response), target_id)

        connection.write_message(json.dumps({'send': {'id': target_id, 'data': None}}))
        response = yield connection.read_message()
        self._test_error(json.loads(response), target_id)

        connection.close()

    @gen_test
    def test_data_received(self):
        connection1 = yield self._connect()

        connection1.write_message(json.dumps({'join': {'self': 1, 'other': [2]}}))
        response = yield connection1.read_message()

        target_id = json.loads(response)['join']['id']

        connection2 = yield self._connect()

        connection2.write_message(json.dumps({'join': {'self': 1, 'other': [2]}}))
        response = yield connection2.read_message()

        sender_id = json.loads(response)['join']['id']

        connection2.write_message(json.dumps({'send': {'id': target_id, 'data': 'test'}}))
        response = yield connection2.read_message()
        self._test_ok(json.loads(response), target_id)

        response = yield connection1.read_message()
        self.assertEqual(json.loads(response), {'data': {'id': sender_id, 'data': 'test'}})

        connection1.close()
        connection2.close()
