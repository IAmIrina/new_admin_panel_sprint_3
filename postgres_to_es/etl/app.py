"""Movies ETL Service."""

import logging
from logging.config import dictConfig
from time import sleep

from config import settings
from config.loggers import LOGGING
from database.pg_database import PGConnection
from processors.enricher import Enricher
from processors.extractor import Extractor
from processors.loader import ESLoader
from processors.transformer import Transformer

dictConfig(LOGGING)
logger = logging.getLogger(__name__)

pg = PGConnection(settings.DATABASES['pg'])

if __name__ == '__main__':

    logger.info('Initializing')

    loader = ESLoader(
        settings.ES['connection'],
        index=settings.ES['index']['name'],
        index_schema=settings.ES['index']['schema'],
    )

    transformer = Transformer(result_handler=loader.proccess)

    enricher = Enricher(
        pg=pg,
        result_handler=transformer.proccess,
        page_size=settings.PAGE_SIZE,
    )

    extractor = Extractor(pg=pg, result_handler=enricher.proccess)

    logger.info('Started')
    while True:
        for entity in settings.ENTITIES:
            extractor.proccess(entity, page_size=settings.PAGE_SIZE)
            sleep(settings.DELAY)
