
"""Backoff decorators"""

from functools import wraps
from time import sleep

import logging
from typing import Any
logger = logging.getLogger(__name__)


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10) -> Any:
    """Retry calling of function.

    The function tries to call an argument function after delay if the argument
    function caused an exception

    Args:
        start_sleep_time: Initial time to repeat.
        factor: Multiplier of time.
        border_sleep_time: Max time.

    Returns:
        Any: Result of calling function.

    """

    def func_wrapper(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            retry = 1
            delay = start_sleep_time
            while True:
                try:
                    return func(self, *args, **kwargs)
                except Exception:
                    logger.exception(
                        'Error in {func}. Next try in {sec} seconds'.format(
                            sec=min(delay, border_sleep_time),
                            func=str(func),
                        ),
                    )
                    sleep(min(delay, border_sleep_time))
                    if delay < border_sleep_time:
                        delay = start_sleep_time * (factor ** retry)
                    retry += 1
        return inner
    return func_wrapper
