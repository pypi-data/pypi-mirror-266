# coding=utf8
""" This pytho file is the prev active coroutine  for all kind of coroutine
"""
from functools import wraps


def prev_active_coroutine(func):
    """
    预激协程的装饰器
    """
    @wraps(func)
    def primer(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return primer


if __name__ == '__main__':

    @prev_active_coroutine
    def average2():
        """calc moving average
        """
        total = 0.0
        count = 0
        average = None
        while True:
            term = yield average
            total += term
            count += 1
            average = total / count
    pass
