from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.websocket import websocket_connect


from app import Application


class TestServer(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def _connect(self, url_path='/api', **kwargs):
        return websocket_connect('ws://127.0.0.1:%u%s' % (self.get_http_port(), url_path), **kwargs)

    @gen_test()
    def _test_request(self, request, response, binary=False):
        connection = yield self._connect()
        connection.write_message(request, binary)
        message = yield connection.read_message()
        self.assertEqual(message, response)
