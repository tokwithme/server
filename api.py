from logging import getLogger

from bson import ObjectId
from bson.errors import InvalidId

from database import Database


log = getLogger(__name__)


class Api():
    def __init__(self):
        self._db = Database()
        self._clients = {}

    def join(self, handler, body):
        if handler.id:
            handler.error('Client %s already joined' % handler.id)
            return

        self_gender = None
        other_gender = None

        if isinstance(body, dict):
            try:
                self_gender = int(body['self'])
                other_gender = [int(gender) for gender in body['other']]
            except TypeError:
                pass

        # TODO: Implement gender validation as function
        if not self_gender or not other_gender or len(other_gender) > 2 or (self_gender != 0 and self_gender != 1):
            handler.error('Incorrect join request: %s' % body)
            return

        for gender in other_gender:
            if gender != 0 and gender != 1:
                handler.error('Incorrect join request: %s' % body)
                return

        client_id = self._db.join(self_gender, other_gender)
        handler.join(client_id, self_gender, other_gender)

        log.debug('Client %s has joined' % client_id)
        handler.write_message({'join': str(client_id)})

    def leave(self, handler, body=None):
        if not handler.id:
            log.warning('Client leaving while not joined')
            return

        self._db.leave(handler.id)
        del self._clients[handler.id]

        log.debug('Client %s has leaved' % handler.id)
        handler.leave()

    def matching(self, handler, body=None):
        if not handler.id:
            handler.error('Client not joined before matching request')
            return

        matching = self._db.matching(handler.id, handler.self_gender, handler.other_gender)

        handler.write_message({'matching': matching})
        log.debug('Sent matching (%u) to %s' % (len(matching), handler.id))

    def data(self, handler, body):
        if not handler.id:
            handler.error('Client not joined before data request')
            return

        target_id = None
        data = None

        if isinstance(body, dict):
            try:
                target_id = ObjectId(body['id'])
                data = body['data']
            except (KeyError, InvalidId):
                pass

        if not target_id or target_id == handler.id or not data or not isinstance(data, str):
            handler.error('Incorrect data request: %s' % body)
            return

        target_client = self._clients.get(target_id)
        if not target_client:
            log.warn('Nonexistent id in data request: %s' % target_id)
            handler.write_message({'data': {'id': str(target_id)}})
            return

        target_client.write_message({'data': {'id': str(handler.id), 'data': data}})
        log.debug('Sent message from %s to %s', handler.id, target_id)
