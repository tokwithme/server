from logging import getLogger

from tornado.websocket import WebSocketHandler

import config

from client import Client


log = getLogger(__name__)


class ApiHandler(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = Client()

    @property
    def client(self):
        return self._client

    def check_origin(self, origin):
        if config.DEBUG:
            return True
        return super().check_origin(origin)

    def open(self):
        log.debug('Client connected')

    def on_message(self, message):
        log.debug('Client message: %s' % message)
        self.application.api.request(self, message)

    def on_close(self):
        self.application.api.leave(self._client)
        log.debug('Client disconnected')
