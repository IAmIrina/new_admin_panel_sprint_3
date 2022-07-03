"""Enrich data process"""

import logging
from logging.config import dictConfig
from typing import Callable
from psycopg2.sql import SQL, Identifier
from config.loggers import LOGGING

from lib import storage
from database.pg_database import PGConnection
from config import settings


dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Enricher(object):
    """Implement getting the additional information about movies

    Attributes:
        pg: Used to work with PG Database.
        callback: Result of proccessing will return to the callable.
        storage: Permanent storage to keep state.
        state: State of the process

    """

    def __init__(self, pg: PGConnection, callback: Callable) -> None:
        """Enricher class constructor.

        Args:
            pg: Used to work with PG Database.
            callback: Result of the proccessing will return to the function.

        """
        self.pg = pg
        self.callback = callback
        self.storage = storage.RedisStorage(settings.REDIS['enricher'])
        self.state = storage.State(self.storage)
        self.proceed()

    def proceed(self):
        """Check the state and proceed to work if there is data in the cashe."""
        if self.state.state.get('pkeys'):
            logger.debug('Data to proceed %s', self.state.state.get('pkeys'))
            self.proccess(
                self.state.state['table'],
                self.state.state['pkeys'],
                self.state.state['page_size'],
            )

    def set_state(self, **kwargs):
        """Set State in cache.

        Args:
            kwargs: Key/value pair to save in cache.

        """
        for key, value in kwargs.items():
            self.state.set_state(key=key, value=value)

    def last_processed_id(self, table):
        """Get last id from cache."""
        last_id = self.state.get_state(table)
        return last_id or ''

    def proccess(self, where_clause_table: str, pkeys: list, page_size: int = 1000) -> None:
        """Run sql to enrich data and pass results to callback.

        Args:
            where_clause_table: Table name for the SQL conditions using in WHERE clause.
            pkeys: Primary keys for the SQL conditions.
            page_size: Count of records.

        """

        logger.debug('Select all movies data by %s', where_clause_table)

        query = SQL("""SELECT
                film_work.id as id,
                film_work.rating as imdb_rating,
                film_work.title as title,
                film_work.description as description,
                film_work.modified,
                COALESCE (
                    json_agg(
                        DISTINCT jsonb_build_object(
                            'role', pfw.role,
                            'id', person.id,
                            'name', person.full_name
                        )
                    ) FILTER (WHERE person.id is not null),
                    '[]'
                ) as persons,
                array_agg(DISTINCT genre.name) as genre
            FROM content.film_work
                LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = film_work.id
                LEFT JOIN content.person ON person.id = pfw.person_id
                LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = film_work.id
                LEFT JOIN content.genre  ON genre.id = gfw.genre_id
            WHERE {where_clause_table}.id in %(pkeys)s
            AND film_work.id::text > %(last_id)s
            GROUP BY film_work.id
            ORDER BY film_work.id
            LIMIT %(page_size)s;
            """).format(
            where_clause_table=Identifier(where_clause_table),
        )

        last_id = self.last_processed_id(where_clause_table)
        while query_result := self.pg._retry_fetchall(
            f"Select all movies data by {where_clause_table}",
            query,
            pkeys=tuple(pkeys),
            last_id=last_id,
            page_size=page_size,
        ):
            last_id = query_result[-1]['id']
            self.set_state(
                table=where_clause_table,
                pkeys=pkeys,
                last_processed_id=last_id,
                page_size=page_size,
            )
            logger.debug('Got additional info for %s  movies', len(query_result))
            self.callback(query_result)

        self.set_state(
            table=None,
            pkeys=None,
            last_processed_id=None,
            page_size=None,
        )
