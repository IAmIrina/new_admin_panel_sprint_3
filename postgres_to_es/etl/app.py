"""Movies ETL Service"""

import logging
from logging.config import dictConfig
from time import sleep

from config import settings
from config.loggers import LOGGING
from database.pg_database import PGConnection
from processors.transformer import Transformer
from processors.extractor import Extractor
from processors.enricher import Enricher
from processors.loader import ESLoader

dictConfig(LOGGING)
logger = logging.getLogger(__name__)

pg = PGConnection(settings.DATABASES['pg'])

if __name__ == '__main__':

    logger.info('Started')

    loader = ESLoader(settings.ES)
    transformer = Transformer(callback=loader.proccess)
    enricher = Enricher(pg=pg, callback=transformer.proccess)
    extractor = Extractor(pg=pg, callback=enricher.proccess)

    while True:
        for entity in settings.ENTITIES:
            extractor.proccess(entity, page_size=settings.PAGE_SIZE)
            sleep(settings.DELAY)
