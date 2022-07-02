"""Data transform for receiving system"""

from datetime import datetime
import logging
from contextlib import contextmanager
from logging.config import dictConfig
from typing import Generator, List
from config import settings

import redis

from config.loggers import LOGGING

from lib import schemas, storage

dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Transformer(object):

    def check_state(self):
        self.status = self.state.get_state('status')
        if self.status == 'processing':
            data = self.state.get_state('data')
            return self.transform(data)
        else:
            return []

    def __init__(self):
        self.storage = storage.RedisStorage(settings.REDIS['transformer'])
        self.state = storage.State(self.storage)

    def get_person_names(self, persons: dict, played_roles: list) -> str:
        names = [person['name'] for person in persons if person['role'] in played_roles]
        return names

    def persons_by_role(self, persons: dict, played_roles: list) -> str:
        persons_info = [schemas.Person(**person).dict() for person in persons if person['role'] in played_roles]
        return persons_info

    def transform(self, movies: dict, index: str = 'movies'):
        self.state.set_state(key='status', value='processing')
        self.state.set_state(key='data', value=[movie for movie in movies])
        for idx, movie in enumerate(movies):
            movies[idx]['director'] = self.get_person_names(movie['persons'], ['director'])
            movies[idx]['actors_names'] = self.get_person_names(movie['persons'], ['actor'])
            movies[idx]['writers_names'] = self.get_person_names(movie['persons'], ['writer'])
            movies[idx]['actors'] = self.persons_by_role(movie['persons'], ['actor'])
            movies[idx]['writers'] = self.persons_by_role(movie['persons'], ['writer'])
            try:
                movies[idx] = schemas.Movie(index=index, **movies[idx]).dict(by_alias=True)
            except Exception:
                logger.exception('Validation data error: %s', movies[idx])
        # self.state.set_state(key='status', value='idle')
        self.state.set_state(key='data', value=None)
        return movies
