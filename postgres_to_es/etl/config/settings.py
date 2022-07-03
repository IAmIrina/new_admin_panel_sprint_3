"""ETL settings."""
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

DEFAULT_REDIS_HOST = '127.0.0.1'
DEFAULT_REDIS_PORT = 6379

DELAY = os.environ.get('DELAY', 1)
PAGE_SIZE = os.environ.get('PAGE_SIZE', 1000)

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
    ),
},
)

REDIS_HOST = types.MappingProxyType({
    'host': DEFAULT_REDIS_HOST,  # os.environ.get('REDIS_HOST', DEFAULT_REDIS_HOST),
    'port': DEFAULT_REDIS_PORT,  # os.environ.get('REDIS_PORT', DEFAULT_REDIS_PORT),
    'password': os.environ.get('REDIS_PASSWORD'),
},
)

REDIS = types.MappingProxyType({
    'extractor': {
        **REDIS_HOST,
        'db': 1,
    },
    'enricher': {
        **REDIS_HOST,
        'db': 2,
    },
    'transformer': {
        **REDIS_HOST,
        'db': 3,
    },
    'loader': {
        **REDIS_HOST,
        'db': 5,
    },
},
)

ENTITIES = ('film_work', 'person', 'genre')
