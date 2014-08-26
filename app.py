import logging
from os import path

from tornado.web import Application as WebApplication
from tornado.ioloop import IOLoop

import config

from api import Api
from handlers.api_handler import ApiHandler
from handlers.main_handler import MainHandler


log = logging.getLogger('app')


class Application(WebApplication):
    def __init__(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )

        super().__init__(
            [
                ('/', MainHandler),
                ('/api', ApiHandler)
            ],
            static_path=path.join(path.dirname(__file__), 'client', 'web', 'build')
        )

        self._api = Api()

    @property
    def api(self):
        return self._api


if __name__ == '__main__':
    Application().listen(config.LISTEN_PORT, config.LISTEN_IP)
    IOLoop.instance().start()
