"""Storage tools."""

import abc
import logging
import pickle
from typing import Any, Callable

from database.backoff_connection import backoff, backoff_reconnect
from redis import Redis

logger = logging.getLogger(__name__)


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Save state to storage"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Get state from storage"""
        pass


class RedisStorage(BaseStorage):
    """Implement Redis Storage tools.

    Attributes:
        connection_settings: Redis db connection parameters.

    """

    def __init__(self, connection_settings: dict) -> None:
        """RedisStorage class constructor.

        Args:
            dict: storage connection settings.

        """
        self.connection_settings = connection_settings
        self._connect()

    @backoff()
    def _connect(self):
        self.redis_adapter = Redis(**self.connection_settings)
        self.redis_adapter.ping()

    @backoff_reconnect()
    def try_command(self, func: Callable, *args, **kwargs) -> Any:
        """Wrap a method to implement backoff reconnection.

        Args:
            func: Decorating method.
            args: Args for the decorating method.
            kwargs: Kwargs for the decorating method.

        Returns:
            Any: Returns of the decorated method.

        """
        return func(*args, **kwargs)

    def save_state(self, state: dict) -> None:
        """Save state to storage.

        Args:
            state: Key/value data for saving in the storage.

        """
        for key, value in state.items():
            self.try_command(self.redis_adapter.set, name=key, value=pickle.dumps(value))

    def retrieve_state(self) -> dict:
        """Load data from the storage.

        Returns:
            dict: Key/value loaded data.

        """
        state = {}
        keys = self.try_command(self.redis_adapter.keys, '*')
        for key in keys:
            value = self.try_command(self.redis_adapter.get, key)
            try:
                state[key.decode('utf-8')] = pickle.loads(value)
            except pickle.UnpicklingError:
                state[key.decode('utf-8')] = value.decode('utf-8') if value else None
        return state


class State(object):
    """Class to work with data.

    Allow to get data from any storage only once during initializing the object.

    Attributes:
        storage: Permanent data storage.
        state: A copy of permanent storage data.

    """

    def __init__(self, storage: BaseStorage) -> None:
        """Constructor of State class.

        Args:
            storage: Permanent data storage.

        """
        self.storage = storage
        self.state = self.storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        """Set and save the key/value pair in permanent storage.

        Args:
            key: Dictionary key for the value.
            value: Value for the key.

        """
        self.state[key] = value
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        """Get the state by key.

        Args:
            key: Key name to retrieve data.

        """
        return self.state.get(key)
