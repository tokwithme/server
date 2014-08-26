import json

from tornado.websocket import WebSocketError

from tests.server import TestServer


class TestRequestFormat(TestServer):
    def test_incorrect_path(self):
        self._connect('/', callback=self.stop)
        self.assertIsInstance(self.wait().exception(), WebSocketError)

    def test_incorrect_json(self):
        self._test_request('', None)
        self._test_request('test', None)
        self._test_request('\x01\x02', None, True)
        self._test_request(json.dumps([]), None)
        self._test_request(json.dumps(''), None)
        self._test_request(json.dumps(True), None)
        self._test_request(json.dumps(1), None)
        self._test_request(json.dumps(None), None)

    def test_incorrect_request(self):
        self._test_request(json.dumps({}), None)
        self._test_request(json.dumps({'test': 'test'}), None)
        self._test_request(json.dumps({'join': 0, 'get': 1}), None)



