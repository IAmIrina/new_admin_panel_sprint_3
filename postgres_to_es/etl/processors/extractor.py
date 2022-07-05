"""Extract data from source"""

import logging
from logging.config import dictConfig
from typing import Callable
from psycopg2.sql import SQL, Identifier
from config.loggers import LOGGING

from lib import storage, sql_templates
from config import settings
from database.pg_database import PGConnection


dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Extractor(object):
    """Extract data from PostgreSQL database.

    Attributes:
        pg: Used to work with PG Database.
        result_handler: Result of proccessing will return to the callable.
        storage: Permanent storage to keep state.
        state: State of the process

    """

    def __init__(self, pg: PGConnection, result_handler: Callable) -> None:
        """Extractor class constructor.

        Args:
            pg: Used to work with PG Database.
            result_handler: Result of proccessing will return to the function.

        """
        self.pg = pg
        self.result_handler = result_handler
        self.storage = storage.RedisStorage(settings.REDIS['extractor'])
        self.state = storage.State(self.storage)

    def get_last_modified(self, table: str) -> str:
        """Get last id from cache.

        Args:
            table: Table name of the modified field.

        Returns:
            str: ISO format date.
        """
        modified = self.state.get_state(table)
        return modified or '1970-01-01'

    def proccess(self, table: str, schema: str = 'content', page_size: int = 100) -> None:
        """Get modified data.

        Args:
            table: Table name for the SQL query.
            schema: Database schema.
            page_size: Count of records.

        """
        logger.debug('Select modified from %s', table)

        query = SQL(sql_templates.get_modified_records).format(
            table=Identifier(schema, table),
        )

        query_result = self.pg._retry_fetchall(
            query,
            modified=self.get_last_modified(table),
            page_size=page_size,
        )

        logger.debug('Got %s records from table %s', len(query_result), table)
        if query_result:
            modified = query_result[-1]['modified']
            self.state.set_state(key=table, value=modified)
            self.result_handler(
                where_clause_table=table,
                pkeys=[record['id'] for record in query_result],
            )
