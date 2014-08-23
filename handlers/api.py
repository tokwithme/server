import json

from logging import getLogger
from tornado.websocket import WebSocketHandler
from bson import ObjectId
from bson.errors import InvalidId


log = getLogger(__name__)


# TODO: Handle uncaught exceptions inside methods
class Api(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = None

    # FIXME: Only for debug
    def check_origin(self, _):
        return True

    # FIXME: Specify code
    def _error(self, reason):
        self.on_close()
        self.close(reason=reason)
        log.error(reason)

    def _join(self, request):
        self._gender = None
        self._other_gender = None

        if isinstance(request, dict):
            try:
                self._gender = int(request['self'])
                self._other_gender = [int(gender) for gender in request['other']]
            except TypeError:
                pass

        # TODO: Implement gender validation as function
        if not self._gender or not self._other_gender or len(self._other_gender) > 2 or (self._gender != 0 and self._gender != 1):
            self._error('Incorrect join request: %s' % request)
            return

        for gender in self._other_gender:
            if gender != 0 and gender != 1:
                self._error('Incorrect join request: %s' % request)
                return

        if not self._id:
            self._id = self.application.db.join(self._gender, self._other_gender)
            self.application.clients[self._id] = self
        else:
            self.application.db.join(self._gender, self._other_gender, self._id)

        self.write_message({'join': str(self._id)})

        log.debug('Client %s has joined' % self._id)

    def _leave(self):
        if not self._id:
            return

        self.application.db.leave(self._id)
        del self.application.clients[self._id]

        log.debug('Client %s has leaved' % self._id)

    def _matching(self):
        if not self._id:
            self._error('Client not joined before list request')
            return

        matching = self.application.db.matching(self._id, self._gender, self._other_gender)
        self.write_message({'matching': matching})

        log.debug('Sent matching (%u) to %s' % (len(matching), self._id))

    def _data(self, request):
        if not self._id:
            self._error('Client not joined before data request')
            return

        target_id = None
        data = None

        if isinstance(request, dict):
            try:
                target_id = ObjectId(request['id'])
                data = request['data']
            except (KeyError, InvalidId):
                pass

        if not target_id or target_id == self._id or not data or not isinstance(data, str):
            self._error('Incorrect data request: %s' % request)
            return

        target_client = self.application.clients.get(target_id)
        if not target_client:
            log.warn('Nonexistent id in data request: %s' % target_id)
            self.write_message({'data': {'id': str(target_id)}})
            return

        target_client.write_message({'data': {'id': str(self._id), 'data': data}})

        log.debug('Sent message from %s to %s', self._id, target_id)

    def open(self):
        log.debug('Client connected')

    # TODO: Limit request rate
    def on_message(self, message):
        log.debug('Client message: %s' % message)

        try:
            request = json.loads(message)
        except (ValueError, TypeError):
            self._error('Failed to parse JSON')
            return

        if not isinstance(request, dict) or len(request.keys()) != 1:
            self._error('Incorrect request')
            return

        if 'join' in request:
            self._join(request['join'])
        elif 'data' in request:
            self._data(request['data'])
        elif 'matching' in request:
            self._matching()
        else:
            self._error('Unknown request type')

    def on_close(self):
        self._leave()
        log.debug('Client disconnected')
