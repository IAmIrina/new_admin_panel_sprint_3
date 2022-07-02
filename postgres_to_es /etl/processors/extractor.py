"""Загрузчик данных в Postgress."""

import logging
from logging.config import dictConfig
from datetime import datetime
from psycopg2.sql import SQL, Identifier
import redis
from config.loggers import LOGGING

from lib import storage
from config import settings
from database.backoff_connection import backoff


dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Extractor(object):

    def __init__(self, pg):
        self.pg = pg
        # storage.JsonFileStorage('extractor_storage')

        self.storage = storage.RedisStorage(settings.REDIS['extractor'])
        self.state = storage.State(self.storage)

    def get_modified(self, table: str, schema: str = 'content', page_size: int = 100) -> list:
        logger.debug('Get modified %s', table)

        modified = self.state.get_state(table)
        if not modified:
            modified = '1970-01-01'

        query = SQL("""Select id, modified from {table}
                where modified > %(modified)s
                ORDER BY modified
                LIMIT %(page_size)s
            """).format(
            table=Identifier(schema, table),
        )

        query_result = self.pg._retry_fetchall('queue_check', query, modified=modified, page_size=page_size)

        if query_result:
            self.state.set_state(key=table, value=query_result[len(query_result) - 1]['modified'])

        logger.debug('Got %s records from table %s', len(query_result), table)
        return [record['id'] for record in query_result]


class Enricher(object):

    # def check_state(self):
    #     self.status = self.state.get_state('status')
    #     if self.status == 'processing':
    #         data = self.state.get_state('data')
    #         return self.transform(data)
    #     else:
    #         return []

    def __init__(self, pg):
        self.pg = pg
        self.storage = storage.RedisStorage(settings.REDIS['enricher'])
        self.state = storage.State(self.storage)

    def get_movies_by(self, where_clause_table: str, pkeys: list, page_size: int = 100) -> list:
        logger.debug('Get movies by %s', where_clause_table)

        query = SQL("""
            SELECT
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

        last_id = self.state.get_state(where_clause_table)

        if not last_id:
            last_id = ''

        while query_result := self.pg._retry_fetchall(
            'queue_check',
            query,
            pkeys=tuple(pkeys),
            last_id=last_id,
            page_size=page_size
        ):
            logger.debug('Got %s  movies', len(query_result))
            last_id = query_result[len(query_result) - 1]['id']
            self.state.set_state(key='table', value=where_clause_table)
            self.state.set_state(key='pkeys', value=pkeys)
            self.state.set_state(key='last_processed_movie_id', value=last_id)
            yield query_result
        self.state.set_state(key='table', value=None)
        self.state.set_state(key='pkeys', value=None)
        self.state.set_state(key='last_processed_movie_id', value=None)
