"""Сheck database availability."""

import logging
import os
import sys
from logging import config
from time import sleep

import psycopg2

pg_settings = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': os.environ.get('DB_PORT', 5432),
    'connect_timeout': 1,
}

LOGGING = {
    'version': 1,
    'formatters': {
        'file': {
            'format': '%(asctime)s: [ %(levelname)s ]: %(module)s : [%(process)d]: %(message)s',
        },
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'file',
            'stream': sys.stdout,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['stdout'],
    },
}

config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    for retry in range(10):
        logger.info(
            'Waiting for DB %s:%s database %s. Timeout %s',
            pg_settings['host'],
            pg_settings['port'],
            pg_settings['dbname'],
            pg_settings['connect_timeout'],
        )
        try:
            connection = psycopg2.connect(**pg_settings)
        except Exception as err:
            if retry == 9:
                logger.error(
                    'Not able to connect to the DB during %s seconds with error %s (%s)',
                    retry,
                    err,
                    err.__class__,
                )
                sys.exit(1)
            sleep(1)
        else:
            logger.info('Successfully connected to the DB %s ', pg_settings['dbname'])
            connection.close()
            break
