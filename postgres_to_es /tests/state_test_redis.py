import inspect
import re
import sys
from json import JSONDecodeError


# TODO: здесь вставьте import для своих файлов State и RedisStorage


class FakeRedis:
    def __init__(self):
        self.data = {}

    def get(self, name):
        return self.data.get(name)

    def set(self, name, value):
        self.data[name] = value


def test_get_empty_state():
    redis_adapter = FakeRedis()
    storage = RedisStorage(redis_adapter)
    state = State(storage)

    assert state.get_state('key') is None


def test_save_new_state():
    redis_adapter = FakeRedis()
    storage = RedisStorage(redis_adapter)
    state = State(storage)

    state.set_state('key', 123)

    assert redis_adapter.data == {'data': '{"key": 123}'}


def test_retrieve_existing_state():
    redis_adapter = FakeRedis()
    redis_adapter.data = {'data': '{"key": 10}'}
    storage = RedisStorage(redis_adapter)
    state = State(storage)

    assert state.get_state('key') == 10


def test_save_state_and_retrieve():
    redis_adapter = FakeRedis()
    storage = RedisStorage(redis_adapter)
    state = State(storage)

    state.set_state('key', 123)

    # Принудительно удаляем объекты
    del state
    del storage

    storage = RedisStorage(redis_adapter)
    state = State(storage)

    assert state.get_state('key') == 123


def test_error_on_corrupted_data():
    try:
        redis_adapter = FakeRedis()
        redis_adapter.data = {'data': '{"key":}'}

        storage = RedisStorage(redis_adapter)
        state = State(storage)

    except JSONDecodeError:
        assert True
        return

    assert False


def run_tests(pattern='test_*'):
    search_pattern = re.compile(pattern)
    for name, func in inspect.getmembers(sys.modules[__name__]):
        if search_pattern.match(name):
            func()


run_tests()
