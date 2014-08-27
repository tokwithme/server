from tornado.websocket import WebSocketError

from tests.server import TestServer


class TestRequestFormat(TestServer):
    def _test_error(self, response):
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 1)
        self.assertIn('error', response)

    def test_incorrect_path(self):
        self._connect('/', callback=self.stop)
        self.assertIsInstance(self.wait().exception(), WebSocketError)

    def test_incorrect_json(self):
        self._test_error(self._request(''))
        self._test_error(self._request('test'))
        self._test_error(self._request('\x01\x02', True))
        self._test_error(self._request([]))
        self._test_error(self._request(''))
        self._test_error(self._request(True))
        self._test_error(self._request(1))
        self._test_error(self._request(None))

    def test_incorrect_request(self):
        self._test_error(self._request({}))
        self._test_error(self._request({'test': 'test'}))
        self._test_error(self._request({'join': 0, 'get': 1}))



