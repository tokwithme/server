from os import environ


DEBUG = int(environ.get('TOKWITHME_DEBUG', 1))

LISTEN_IP = environ.get('OPENSHIFT_PYTHON_IP', '0.0.0.0')
LISTEN_PORT = int(environ.get('OPENSHIFT_PYTHON_PORT', 8000))

DATABASE_URL = environ.get('OPENSHIFT_MONGODB_DB_URL', 'mongodb://localhost:27017')
DATABASE_NAME = environ.get('OPENSHIFT_APP_NAME', 'tokwithme')

MATCHING_MAX_COUNT = 10
