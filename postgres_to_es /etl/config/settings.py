"""Настройки проекта."""
import os
import pathlib
import types

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

ROOTDIR = os.path.join(pathlib.Path(__file__).parent.parent.absolute())

DEFAULT_DB_HOST = '127.0.0.1'
DEFAULT_DB_PORT = 5432
DEFAULT_ES_HOST = 'http://localhost'
DEFAULT_ES_PORT = 9200


DATABASES = types.MappingProxyType({
    'pg': {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': '130.193.42.101',  # os.environ.get('DB_HOST', DEFAULT_DB_HOST),
        'port': os.environ.get('DB_PORT', DEFAULT_DB_PORT),
        'connect_timeout': int(os.environ.get('CONNECT_TIMEOUT', '1')),
    },
})
ES = types.MappingProxyType({
    'hosts': '{host}:{port}'.format(
        host='http://127.0.0.1',  # os.environ.get('ES_HOST', DEFAULT_ES_HOST),
        port=9200,  # os.environ.get('ES_PORT', DEFAULT_ES_PORT),
    )
}
)
print(ES)
ENTITIES = ('film_work', 'person', 'genre')
