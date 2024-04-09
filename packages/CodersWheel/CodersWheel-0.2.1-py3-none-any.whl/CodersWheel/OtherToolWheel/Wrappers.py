# -*- coding:utf-8 -*-
from CacheFunctions import LRUDict, LrudictUnpickled
# from functools import wraps


def LRUCache_PureDict(capacity=500):
    memo = {}

    def Cache(func):

        # @wraps(func)
        def _wrapper(*args):
            res = memo.get(args, None)
            if res is not None:
                pass
                # return res
            else:
                res = func(*args)
                memo[args] = res
            return res
        return _wrapper
    return Cache


def LRUCache(capacity=500):
    memo = LRUDict(capacity, Pickled=False)

    def Cache(func):
        # @wraps(func)
        def _wrapper(*args):
            res = memo.get(args, None)
            if res is not None:
                pass
                # return res
            else:
                res = func(*args)
                memo[args] = res
            return res
        return _wrapper
    return Cache


def LRUCache_UnPickled(capacity=500):
    memo = LrudictUnpickled(capacity)

    def Cache(func):
        # @wraps(func)
        def _wrapper(*args):
            res = memo.get(args, None)
            if res is not None:
                pass
                # return res
            else:
                res = func(*args)
                memo[args] = res
            return res
        return _wrapper
    return Cache


if __name__ == '__main__':
    @LRUCache
    def fib(n):
        if n <= 1:
            return n
        else:
            return fib(n - 1) + fib(n - 2)
    print([fib(i) for i in list(range(31))])
