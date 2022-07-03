"""Transform data process."""

import logging
from logging.config import dictConfig
from typing import Callable
from config import settings


from config.loggers import LOGGING

from lib import schemas, storage

dictConfig(LOGGING)
logger = logging.getLogger(__name__)


class Transformer(object):
    """Implement transform data to Elasticksearch index format.

    Attributes:
        callback: Result of proccessing will return to the callable.
        storage: Permanent storage to keep state.
        state: State of the process

    """

    def __init__(self, callback: Callable) -> None:
        """Transformer class constructor.

        Args:
            callback: Result of the proccessing will be returned to the function.

        """

        self.storage = storage.RedisStorage(settings.REDIS['transformer'])
        self.state = storage.State(self.storage)
        self.callback = callback
        self.proceed()

    def proceed(self) -> None:
        """Check the state and proceed to work if there is data in the cashe."""

        if self.state.state.get('data'):
            logger.debug('Data to proceed %s', self.state.state.get('data'))
            self.proccess(
                movies=self.state.state.get('data'),
                index=self.state.state.get('index'),
            )

    def set_state(self, **kwargs) -> None:
        """Set State in cache.

        Args:
            kwargs: Key/value pair to save in cache.

        """
        for key, value in kwargs.items():
            self.state.set_state(key=key, value=value)

    def get_person_names(self, persons: dict, played_roles: list = None) -> str:
        """Get list of persons names.

        Args:
            persons: List of Persons to extract names
            played_roles: List of Roles to filter.

        """
        if played_roles:
            return [person['name'] for person in persons if person['role'] in played_roles]
        else:
            return [person['name'] for person in persons]

    def persons_by_role(self, persons: dict, played_roles: list = None) -> dict:
        """Get list of persons info.

        Args:
            persons: List of Persons to extract names
            played_roles: List of Roles to filter.

        """
        if played_roles:
            return [schemas.Person(**person).dict() for person in persons if person['role'] in played_roles]
        else:
            return [schemas.Person(**person).dict() for person in persons]

    def proccess(self, movies: dict, index: str = 'movies') -> None:
        """Transform data and pass results to callback.

        Args:
            movies: movies data to transform.
            index: name of Elasticsearch index.

        """
        self.set_state(data=[movie for movie in movies], index=index)
        for idx, movie in enumerate(movies):
            try:
                movies[idx] = schemas.Movie(
                    **movies[idx],
                    director=self.get_person_names(movie['persons'], ['director']),
                    actors_names=self.get_person_names(movie['persons'], ['actor']),
                    writers_names=self.get_person_names(movie['persons'], ['writer']),
                    actors=self.persons_by_role(movie['persons'], ['actor']),
                    writers=self.persons_by_role(movie['persons'], ['writer']),
                    index=index,
                ).dict(by_alias=True)
            except Exception:
                logger.exception('Validation data error: %s', movies[idx])
        self.set_state(data=None)
        self.callback(movies)
