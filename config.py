from os import environ


LISTEN_IP = environ.get('OPENSHIFT_PYTHON_IP', '127.0.0.1')
LISTEN_PORT = int(environ.get('OPENSHIFT_PYTHON_PORT', 8000))

DATABASE_URL = environ.get('OPENSHIFT_MONGODB_DB_URL', 'mongodb://localhost:27017')
DATABASE_NAME = environ.get('OPENSHIFT_APP_NAME', 'tokwithme')
DATABASE_RETRY_COUNT = 3
