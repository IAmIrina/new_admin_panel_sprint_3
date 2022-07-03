"""Загрузчик данных в Postgress."""

import logging
from logging.config import dictConfig

import psycopg2
import psycopg2.sql
from psycopg2.extras import RealDictCursor

from config.loggers import LOGGING

from database.backoff_connection import backoff


dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class PGConnection(object):
    """PG Connection class for PostgreSQL.

    The class implements backoff and wraps up  execution sql queries

    Attributes:
        pg_settings : settings for PG connection.

    """

    @backoff()
    def connect(self) -> None:
        """PG connection function with backoff wrapper."""
        logger.debug(
            'Connecting to the DB %s. Timeout %s',
            self.pg_settings['dbname'],
            self.pg_settings['connect_timeout'],
        )
        self.connection = psycopg2.connect(**self.pg_settings)
        logger.debug('Connected to the DB %s', self.pg_settings['dbname'])

    def __init__(self, pg_settings: dict) -> None:
        """PGConnection class constructor.
        Args:
            pg_settings:  settings for PG connection.
        """
        self.pg_settings = pg_settings
        self.connect()

    def disconnect(self) -> None:
        """Close PG connection."""
        try:
            self.connection.close()
            logger.debug('Disconnect DB')
        except Exception:
            pass

    def __del__(self) -> None:
        """Delete object event wrapper.

        Close PG connection when object is ready for deleting.

        """
        self.disconnect()

    def _retry_fetchall(self, sql_id: str, sql: psycopg2.sql.Composed, **kwargs) -> RealDictCursor:
        """SQL query executor.

        Execute passed in args sql query and return results.

        Args:
            sql_id: Query id for logging.
            sql: SQL query.
            kwargs: keywordargs to pass into sql quey.

        Returns:
            RealDictCursor: records from database.

        """
        while True:
            try:
                with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(sql, (kwargs))
                    return cursor.fetchall()
            except Exception:
                logger.exception('Error to check data %s, SQL %s', sql_id, sql)
                self.disconnect()
                self.connect()
