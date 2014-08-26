import config

from logging import getLogger
from pymongo import MongoClient


log = getLogger(__name__)


class Database:
    def __init__(self):
        connection = MongoClient(config.DATABASE_URL)
        self._db = connection[config.DATABASE_NAME]
        connection.drop_database(self._db)

    def join(self, self_gender, other_gender, client_id=None):
        gender = {
            'self': self_gender,
            'other': other_gender
        }

        if not client_id:
            return self._db.clients.insert({'gender': gender})

        self._db.clients.update(client_id, {'$set': {'gender': gender}})

    def leave(self, client_id):
        self._db.clients.remove(client_id)

    def matching(self, client_id, self_gender, other_gender):
        spec = {
            '_id': {'$ne': client_id},
            'gender.self': {'$in': other_gender},
            'gender.other': self_gender
        }

        return [match for match in self._db.find(spec, fields=[])]
