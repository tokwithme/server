import json
from logging import getLogger

from tornado.websocket import WebSocketHandler


log = getLogger(__name__)


# TODO: Handle uncaught exceptions inside methods
class ApiHandler(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._id = None
        self._gender = None
        self._other_gender = None

    @property
    def id(self):
        return self._id

    @property
    def gender(self):
        return self._gender

    @property
    def other_gender(self):
        return self._other_gender

    # FIXME: Only for debug
    def check_origin(self, _):
        return True

    # FIXME: Specify code
    def error(self, reason):
        self.on_close()
        self.close(reason=reason)
        log.error(reason)

    def open(self):
        log.debug('Client connected')

    # TODO: Limit request rate
    def on_message(self, message):
        log.debug('Client message: %s' % message)

        try:
            request = json.loads(message)
        except (ValueError, TypeError):
            self.error('Failed to parse JSON')
            return

        if not isinstance(request, dict) or len(request) != 1:
            self.error('Incorrect request')
            return

        method_name = next(iter(request))
        method = getattr(self.application.api, method_name, None)

        if method and not method_name.startswith('_'):
            method(self, request[method_name])
        else:
            self.error('Unknown request')

    def on_close(self):
        self.application.api.leave(self)
        log.debug('Client disconnected')

    def join(self, client_id, self_gender, other_gender):
        self._id = client_id
        self._gender = self_gender
        self._other_gender = other_gender

    def leave(self):
        self._id = None
        self._gender = None
        self._other_gender = None
