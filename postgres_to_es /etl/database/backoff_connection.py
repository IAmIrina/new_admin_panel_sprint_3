from functools import wraps
from time import sleep

import logging
from logging.config import dictConfig
from config.loggers import LOGGING

dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.

    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """
    def func_wrapper(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            retry = 1
            delay = start_sleep_time
            while True:
                try:
                    func(self, *args, **kwargs)
                except Exception as err:
                    logger.exception(
                        'Error. Next try in {sec} seconds'.format(
                            sec=min(delay, border_sleep_time))
                    )
                    sleep(min(delay, border_sleep_time))
                    if delay < border_sleep_time:
                        delay = start_sleep_time * (factor ** retry)
                    retry += 1
                else:
                    break
        return inner
    return func_wrapper


# @backoff()
# def myfunct():
#     if random.randint(3, 9) < 6:
#         print('Exception')
#         raise Exception()
#     else:
#         print('bye')


# myfunct()
