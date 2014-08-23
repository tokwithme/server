from functools import wraps
from logging import getLogger
from time import sleep

from pymongo import MongoClient
from pymongo.errors import AutoReconnect, ConnectionFailure

import config


log = getLogger(__name__)


# TODO: Move to Database
def catch_exceptions(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        for i in range(config.DATABASE_RETRY_COUNT):
            try:
                return method(self, *args, **kwargs)
            except AutoReconnect:
                time = 2 ** i
                log.warn('Database connection lost. Retrying after %u sec' % time)
                # FIXME: Don't block Tornado's ioloop
                sleep(time)
            except:
                raise

        raise ConnectionFailure
    return wrapper


# TODO: Implement as context manager
class Database:
    def __init__(self):
        self._connection = None

        for i in range(config.DATABASE_RETRY_COUNT):
            try:
                self._connection = MongoClient(config.DATABASE_URL)
                break
            except ConnectionFailure:
                time = 2 ** i
                log.warn('Database connection failure. Retrying after %u sec' % time)
                sleep(time)
            except:
                raise

        if not self._connection:
            raise ConnectionFailure

        self._db = self._connection[config.DATABASE_NAME]
        self._connection.drop_database(self._db)

    def __del__(self):
        if self._connection:
            self._connection.close()

    @catch_exceptions
    def join(self, self_gender, other_gender, client_id=None):
        gender = {
            'self': self_gender,
            'other': other_gender
        }

        if not client_id:
            return self._db.clients.insert({'gender': gender})

        self._db.clients.update(client_id, {'$set': {'gender': gender}})

    @catch_exceptions
    def leave(self, client_id):
        self._db.clients.remove(client_id)

    @catch_exceptions
    def matching(self, client_id, self_gender, other_gender):
        spec = {
            '_id': {'$ne': client_id},
            'gender.self': {'$in': other_gender},
            'gender.other': self_gender
        }

        return [match for match in self._db.find(spec, fields=[])]
