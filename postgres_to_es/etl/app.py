"""Movies ETL Service."""

import logging
from logging.config import dictConfig
from time import sleep

from config import settings
from lib.loggers import LOGGING
from database.pg_database import PGConnection
from processors.enricher import Enricher
from processors.extractor import Extractor
from processors.loader import ESLoader
from processors.transformer import Transformer

dictConfig(LOGGING)
logger = logging.getLogger(__name__)

pg = PGConnection(settings.postgres.dict())


if __name__ == '__main__':

    logger.info('Initializing')

    loader = ESLoader(
        redis_settings=settings.cache.loader,
        transport_options=settings.es.connection.dict(),
        index=settings.es.index,
        index_schema=settings.es.index_schema,
    )
    transformer = Transformer(
        redis_settings=settings.cache.transformer,
        result_handler=loader.proccess,
    )

    enricher = Enricher(
        pg=pg,
        redis_settings=settings.cache.enricher,
        result_handler=transformer.proccess,
        page_size=settings.page_size,
    )

    extractor = Extractor(
        pg=pg,
        redis_settings=settings.cache.extractor,
        result_handler=enricher.proccess,
    )

    logger.info('Started')
    while True:
        for entity in settings.entities:
            extractor.proccess(entity, page_size=settings.page_size)
            sleep(settings.delay)
