import logging
import os.path

from tornado.web import Application as WebApplication
from tornado.ioloop import IOLoop

import config

from database import Database
from handlers.api import Api as ApiHandler
from handlers.main import Main as MainHandler

log = logging.getLogger('app')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)


class Application(WebApplication):
    def __init__(self, db):
        super().__init__(
            [
                ('/', MainHandler),
                ('/api', ApiHandler)
            ],
            static_path=os.path.join(os.path.dirname(__file__), 'client', 'web', 'build')
        )

        self._db = db
        self._clients = {}

    @property
    def db(self):
        return self._db

    @property
    def clients(self):
        return self._clients


if __name__ == '__main__':
    Application(Database()).listen(config.LISTEN_PORT, config.LISTEN_IP)
    IOLoop.instance().start()
