"""Загрузчик данных в Postgress."""

import logging
from logging.config import dictConfig
from typing import Generator, List

import psycopg2
from psycopg2.sql import SQL, Identifier
from psycopg2.extras import RealDictCursor

from config.loggers import LOGGING

from database.backoff_connection import backoff

dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class PGConnection(object):
    """Класс загрузки данных в PostgreSQL.
    Attributes:
        connection : Подключение к PostgreSQL.
    """
    @backoff()
    def connect(self) -> None:
        logger.debug(
            'Connecting to the DB %s. Timeout %s',
            self.pg_settings['dbname'],
            self.pg_settings['connect_timeout']
        )
        self.connection = psycopg2.connect(**self.pg_settings)
        logger.debug('Connected to the DB %s', self.pg_settings['dbname'])

    def __init__(self, pg_settings: dict) -> None:
        """Конструктор класса  PostgresSaver для инициализации объекта.
        Args:
            connection: Подключение к PostgreSQL.
        """
        self.pg_settings = pg_settings
        self.connect()

    def disconnect(self) -> None:
        try:
            self.connection.close()
            logger.debug('Disconnect DB')
        except Exception:
            pass

    def __del__(self) -> None:
        self.disconnect()

    def _retry_fetchall(self, sql_id, sql, retry: int = 3, *args, **kwargs) -> list:
        while retry > 0:
            try:
                with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(sql, (kwargs))
                    result = cursor.fetchall()
            except Exception as err:
                logger.exception('Error to check data, SQL %s', sql)
                retry -= 1
                self.disconnect()
                self.connect()
            else:
                return result
        return []
