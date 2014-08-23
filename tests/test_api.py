import json

from tornado.testing import AsyncTestCase, gen_test
from tornado.websocket import websocket_connect, WebSocketError


# TODO: Start and stop server automatically
class TestApi(AsyncTestCase):
    def _connect(self, url='ws://127.0.0.1:8000/api'):
        return websocket_connect(url)

    @gen_test
    def test_incorrect_path(self):
        # FIXME: Use assertRaises
        try:
            yield self._connect('ws://127.0.0.1:8000/')
        except WebSocketError:
            return
        else:
            self.fail()

    # FIXME: Remove code duplication
    @gen_test
    def test_incorrect_json(self):
        connection = yield self._connect()
        connection.write_message('')
        response = yield connection.read_message()
        self.assertEqual(response, None)

        connection = yield self._connect()
        connection.write_message('test')
        response = yield connection.read_message()
        self.assertEqual(response, None)

        connection = yield self._connect()
        connection.write_message('\x01\x02', True)
        response = yield connection.read_message()
        self.assertEqual(response, None)

        connection = yield self._connect()
        connection.write_message(json.dumps([]))
        response = yield connection.read_message()
        self.assertEqual(response, None)

        connection = yield self._connect()
        connection.write_message(json.dumps(''))
        response = yield connection.read_message()
        self.assertEqual(response, None)

        connection = yield self._connect()
        connection.write_message(json.dumps(True))
        response = yield connection.read_message()
        self.assertEqual(response, None)

        connection = yield self._connect()
        connection.write_message(json.dumps(1))
        response = yield connection.read_message()
        self.assertEqual(response, None)

    # FIXME: Remove code duplication
    @gen_test
    def test_incorrect_request(self):
        connection = yield self._connect()
        connection.write_message(json.dumps({}))
        response = yield connection.read_message()
        self.assertEqual(response, None)

        connection = yield self._connect()
        connection.write_message(json.dumps({'test': 'test'}))
        response = yield connection.read_message()
        self.assertEqual(response, None)

        connection = yield self._connect()
        connection.write_message(json.dumps({'join': 0, 'get': 1}))
        response = yield connection.read_message()
        self.assertEqual(response, None)


