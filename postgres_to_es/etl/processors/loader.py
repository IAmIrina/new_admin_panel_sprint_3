"""Load data process"""

from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers

import logging
from logging.config import dictConfig
from config.loggers import LOGGING

from lib import storage
from database.backoff_connection import backoff
from config import settings


dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class ESLoader(object):
    """Load data to Elastic Search.

    Attributes:
        client: Elisticsearch client.
        storage: Permanent storage to keep state.
        state: State of the process

    """

    def __init__(self, transport_options: dict) -> None:
        """ESLoader class constructor.

        Args:
            transport_options: Elasticsearch connection parameters.

        """
        self.client = Elasticsearch(**transport_options)
        self.storage = storage.RedisStorage(settings.REDIS['loader'])
        self.state = storage.State(self.storage)
        self.proceed()

    def proceed(self):
        """Check the state and proceed to work if there is data in the cache."""
        if self.state.state.get('data'):
            logger.debug('Data to proceed %s', self.state.state.get('data'))
            self.proccess(self.state.state['data'])

    def proccess(self, data: dict) -> None:
        """Load data to Elasticseatch.

        Args:
            data: Loading to ES data.

        """
        self.state.set_state(key='data', value=data)
        self.bulk(data)
        self.state.set_state(key='data', value=None)

    @ backoff()
    def bulk(self, data: dict):
        """Bulk data to ES with backoff implementation.

        Args:
            data: Loading to ES data.

        """
        _, errors = helpers.bulk(self.client, data, stats_only=False)
        if errors:
            failed = self.state.get_state('failed') or []
            failed.append(
                {
                    'time': datetime.now(),
                    'details': errors,
                },
            )
            self.state.set_state(key='failed', value=failed)
            logger.error('Error to bulk data %s', errors)
