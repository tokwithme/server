from logging import getLogger

from pymongo import MongoClient

import config


log = getLogger(__name__)


class Database:
    def __init__(self):
        connection = MongoClient(config.DATABASE_URL)
        self._db = connection[config.DATABASE_NAME]
        connection.drop_database(self._db)

        # TODO: Create index

    def join(self, self_gender, other_gender):
        document = {
            'gender': {
                'self': self_gender,
                'other': other_gender
            }
        }

        return self._db.clients.insert(document)

    def leave(self, client_id):
        self._db.clients.remove(client_id)

    def matching(self, client_id, self_gender, other_gender):
        spec = {
            '_id': {'$ne': client_id},
            'gender.self': {'$in': other_gender},
            'gender.other': self_gender
        }

        return [match['_id'] for match in self._db.clients.find(spec, fields=[])]
