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
