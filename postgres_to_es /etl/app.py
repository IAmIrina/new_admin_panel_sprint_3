"""Мигратор movies_database из SQLite в PostgreSQL."""

import logging
from logging.config import dictConfig
from time import sleep

from config import settings
from config.loggers import LOGGING
from database.pg_database import PGConnection
from lib.transform import Transformer
from lib.extract import Extractor, Enricher
from lib.elastic_load import ESLoader

dictConfig(LOGGING)
logger = logging.getLogger(__name__)

pg = PGConnection(settings.DATABASES['pg'])
extractor = Extractor(pg)
enricher = Enricher(pg)
loader = ESLoader(settings.ES)

# SQL_SETTINGS = settings.DATABASES['sqlite']
PG_SETTINGS = settings.DATABASES['pg']


# def load_from_pg(pg_conn: _connection) -> None:
#     """Основной метод загрузки данных из PostgreSQL.
#     Args:
#         pg_conn: установленное подключение PostgreSQL источником
#     """
#     postgres_saver = PostgresSaver(pg_conn)
#     sqlite_loader = SQLiteLoader(connection)

#     postgres_saver.truncate_tables(tables=[table for table, _ in settings.MIGRATIONS])

#     for table, schema in settings.MIGRATIONS:
#         logger.info('Table %s in process', table)
#         query_result = sqlite_loader.load_data(table, schema)

#         for batch in query_result:
#             if not postgres_saver.save_data_to(table, batch):
#                 return


if __name__ == '__main__':

    logger.info('Started')
    logger.debug('PG settings %s', settings.DATABASES['pg'])
    transformer = Transformer()
    while True:
        for entity in settings.ENTITIES:
            extracted = extractor.get_modified(entity, page_size=2)
            if not extracted:
                continue

            enriched = enricher.get_movies_by(where_clause_table=entity, pkeys=extracted, page_size=2)
            for batch in enriched:
                transform_movies = transformer.transform(batch)
                # break
                loader.load_data(transform_movies)
                sleep(0.1)
                break
        break
        sleep(0.5)
    logger.info('Finished')
