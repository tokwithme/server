from logging import getLogger
import json

from bson import ObjectId
from bson.errors import InvalidId

from database import Database


log = getLogger(__name__)


class Api():
    def __init__(self):
        self._db = Database()
        self._clients = {}

    def request(self, handler, body):
        try:
            request = json.loads(body)
        except (ValueError, TypeError):
            Api._error_response(handler, 'Failed to parse JSON')
            return

        if not isinstance(request, dict) or len(request) != 1:
            Api._error_response(handler, 'Incorrect request')
            return

        method_name = next(iter(request))
        method = getattr(self, '_%s_request' % method_name, None)

        if method and not method_name.startswith('_'):
            method(handler, request[method_name])
        else:
            Api._error_response(handler, 'Unknown request')

    def leave(self, client):
        if not client.id:
            return

        self._db.leave(client.id)
        del self._clients[client.id]

        log.debug('Client %s has leaved' % client.id)
        client.leave()

    def _join_request(self, handler, body):
        if handler.client.id:
            Api._join_response(handler, None, 'Client already joined')
            return

        self_gender = None
        other_gender = None

        if isinstance(body, dict):
            try:
                self_gender = int(body['self'])
                other_gender = [int(gender) for gender in body['other']]
            except (ValueError, TypeError):
                pass

        # TODO: Implement gender validation as function
        if not self_gender or not other_gender or len(other_gender) > 2 or (self_gender != 1 and self_gender != 2):
            Api._join_response(handler, None, 'Incorrect join request')
            return

        for gender in other_gender:
            if gender != 1 and gender != 2:
                Api._join_response(handler, None, 'Incorrect join request')
                return

        client_id = self._db.join(self_gender, other_gender)
        handler.client.join(client_id, self_gender, other_gender)
        self._clients[client_id] = handler

        Api._join_response(handler, client_id)
        log.debug('Client %s has joined' % client_id)

    def _leave_request(self, handler, body=None):
        if handler.client.id:
            self.leave(handler.client)
            self._leave_response(handler, True)
        else:
            self._leave_response(handler, False, 'Client leaving while not joined')

    def _matching_request(self, handler, body=None):
        if not handler.client.id:
            Api._matching_response(handler, None, 'Client not joined before matching request')
            return

        matching = self._db.matching(handler.client.id, handler.client.self_gender, handler.client.other_gender)

        Api._matching_response(handler, [str(match) for match in matching])
        log.debug('Sent matching (%u) to %s' % (len(matching), handler.client.id))

    def _send_request(self, handler, body):
        target_id = ''
        data = ''

        if isinstance(body, dict):
            try:
                target_id = ObjectId(body['id'] or '')
                data = body['data']
            except (KeyError, TypeError, InvalidId):
                pass

        if not target_id or target_id == handler.client.id or not data or not isinstance(data, str):
            Api._send_response(handler, False, target_id, 'Incorrect send request')
            return

        if not handler.client.id:
            Api._send_response(handler, False, target_id, 'Client not joined before send request')
            return

        target = self._clients.get(target_id)
        if target:
            Api._data_response(target, handler.client.id, data)

        Api._send_response(handler, True, target_id)
        log.debug('Sent message from %s to %s', handler.client.id, target_id)

    @staticmethod
    def _error_response(handler, description):
        log.error(description)
        handler.write_message({'error': description})

    @staticmethod
    def _join_response(handler, client_id, reason=''):
        if client_id is None:
            log.error(reason)
            handler.write_message({'join': {'ok': False, 'reason': reason}})
        else:
            handler.write_message({'join': {'ok': True, 'id': str(client_id)}})

    @staticmethod
    def _leave_response(handler, ok, reason=''):
        if not ok:
            log.error(reason)
            handler.write_message({'leave': {'ok': False, 'reason': reason}})
        else:
            handler.write_message({'leave': {'ok': True}})

    @staticmethod
    def _matching_response(handler, matching, reason=''):
        if matching is None:
            log.error(reason)
            handler.write_message({'matching': {'ok': False, 'reason': reason}})
        else:
            handler.write_message({'matching': {'ok': True, 'list': matching}})

    @staticmethod
    def _send_response(handler, ok, target_id, reason=''):
        if not ok:
            log.error(reason)
            handler.write_message({'send': {'ok': False, 'id': str(target_id), 'reason': reason}})
        else:
            handler.write_message({'send': {'ok': True, 'id': str(target_id)}})

    @staticmethod
    def _data_response(handler, sender_id, data):
        handler.write_message({'data': {'id': str(sender_id), 'data': data}})
