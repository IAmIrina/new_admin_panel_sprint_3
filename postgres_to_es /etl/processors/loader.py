"""Загрузчик данных в Postgress."""

from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch import helpers

import logging
from logging.config import dictConfig
from config.loggers import LOGGING

from lib import storage
from database.backoff_connection import backoff
import redis
from config import settings


dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class ESLoader(object):

    def __init__(self, transport_options: dict):
        self.client = Elasticsearch(**transport_options)
        self.storage = storage.RedisStorage(settings.REDIS['loader'])
        self.state = storage.State(self.storage)

    def load_data(self, data: dict):
        self.state.set_state(key='data', value=data)
        self.bulk(data)
        self.state.set_state(key='data', value=None)

    @ backoff()
    def bulk(self, data: dict):
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
