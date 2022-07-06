"""Enrich data process."""

import logging
from logging.config import dictConfig
from typing import Callable

from lib.loggers import LOGGING
from database.pg_database import PGConnection
from lib import sql_templates, storage
from psycopg2.sql import SQL, Identifier

dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Enricher(object):
    """Implement getting additional information about movies.

    Attributes:
        pg: Used to work with PG Database.
        result_handler: Result of proccessing will return to the callable.
        storage: Permanent storage to keep state.
        state: State of the process
        page_size: Count of records to return.

    """

    def __init__(self, pg: PGConnection, redis_settings: dict, result_handler: Callable, page_size: int = 100) -> None:
        """Enricher class constructor.

        Args:
            pg: Used to work with PG Database.
            result_handler: Result of the proccessing will return to the function.
            redis_settings: Redis connection settings.

        """
        self.pg = pg
        self.result_handler = result_handler
        self.storage = storage.RedisStorage(redis_settings)
        self.state = storage.State(self.storage)
        self.page_size = page_size
        self.proceed()

    def proceed(self) -> None:
        """Check the state and proceed to work if there is data in the cashe."""
        if self.state.state.get('pkeys'):
            logger.debug('Data to proceed %s', self.state.state.get('pkeys'))
            self.proccess(
                self.state.state['table'],
                self.state.state['pkeys'],
                self.state.state['page_size'],
            )

    def set_state(self, **kwargs) -> None:
        """Set State in cache.

        Args:
            kwargs: Key/value pair to save in cache.

        """
        for key, value in kwargs.items():
            self.state.set_state(key=key, value=value)

    def proccess(self, where_clause_table: str, pkeys: list) -> None:
        """Run sql to enrich data and pass results to result_handler.

        Args:
            where_clause_table: Table name for the SQL conditions using in WHERE clause.
            pkeys: Primary keys for the SQL conditions.

        """

        logger.debug('Select all movies data by %s', where_clause_table)

        query = SQL(sql_templates.get_movie_info_by_id).format(
            where_clause_table=Identifier(where_clause_table),
        )

        while query_result := self.pg.retry_fetchall(
            query,
            pkeys=tuple(pkeys),
            last_id=self.state.get_state('last_processed_id') or '',
            page_size=self.page_size,
        ):
            self.set_state(
                table=where_clause_table,
                pkeys=pkeys,
                last_processed_id=query_result[-1]['id'],
                page_size=self.page_size,
            )
            logger.debug('Got additional info for %s  movies', len(query_result))
            self.result_handler(query_result)

        self.set_state(
            table=None,
            pkeys=None,
            last_processed_id=None,
            page_size=None,
        )
