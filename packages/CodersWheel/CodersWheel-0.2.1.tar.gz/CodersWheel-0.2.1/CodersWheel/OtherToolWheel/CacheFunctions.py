# -*- coding:utf-8 -*-
from collections import OrderedDict
from functools import wraps
import time

try:
    import cPickle as pickle
except ImportError as e:  # pragma: no cover
    import pickle


# this is main function for creating inherit cache system via
# decorator
# Black magic
#
#
# LFUCache(Least Frequently Used (LFU) cache implementation.)
# LRUCache(Least Recently Used (LRU) cache implementation.)
# RRCache(Random Replacement (RR) cache implementation.)
# TTLCAche(LRU Cache implementation with per-item time-to-live (TTL) value.)


class LrudictUnpickled(OrderedDict):
    # this is the original dict for cache or LRU function
    # it will set up capacity ,default as 250, and if the length of current dict
    # is large than the value of parameter of capacity, then the old key-value will
    # be deleted and receive the one

    __slots__ = ('_capacity')

    def __init__(self, capacity=250):
        super(LrudictUnpickled, self).__init__()
        self._capacity = capacity

    def __setitem__(self, key, value):
        containsKey = 1 if key in self else 0
        if len(self) - containsKey >= self._capacity:
            last = self.popitem(last=False)

            # print 'remove:', last
        if containsKey:
            del self[key]

            # print 'set:', (key, value)
        else:
            pass
            # print 'add:', (key, value)
        OrderedDict.__setitem__(self, key, value)


class LRUDict(OrderedDict):
    __slots__ = ('_capacity')

    def __init__(self, capacity=250, Pickled=True):
        super(LRUDict, self).__init__()
        self._capacity = capacity
        self.save_func = self.picklesave if Pickled else self.normalsave
        self.load_func = self.pickleload if Pickled else self.normalload

    def __setitem__(self, key, value):
        containsKey = 1 if key in self else 0
        if len(self) - containsKey >= self._capacity:
            self.popitem(last=False)

            # remove
            # print 'remove:', last
        if containsKey:
            del self[key]
            # print 'set:', (key, value)
        else:
            pass
            # print 'add:', (key, value)
        # pickled_value = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        # pickled_value = self.save_func(value)
        OrderedDict.__setitem__(self, key, self.save_func(value))

    def __getitem__(self, key):

        pickled_value = OrderedDict.__getitem__(self, key)
        return self.load_func(pickled_value)
        # try:
        #     return pickle.loads(value)
        # except (KeyError, pickle.PickleError):
        #     return None

    def normalload(self, value):
        return value

    def normalsave(self, value):
        return value

    def picklesave(self, value):
        return pickle.dumps(value, pickle.HIGHEST_PROTOCOL)

    def pickleload(self, pickled_value):
        try:
            return pickle.loads(pickled_value, pickle.HIGHEST_PROTOCOL)
        except (KeyError, pickle.PickleError):
            return None
        # ------------------


class BaseCacheClass(object):
    """Baseclass for the cache systems.  All the cache systems implement this
    API or a superset of it.
    :param default_timeout: the default timeout (in seconds) that is used if
                            no timeout is specified on :meth:`set`. A timeout
                            of 0 indicates that the cache never expires.
    """

    def __init__(self, default_timeout=300):
        self.default_timeout = default_timeout

    def set_default_timeout(self, timeout):
        self.default_timeout = timeout if isinstance(
            timeout, (int, float)) else 300

    def get_single(self, key):
        return None

    def get(self, *keys):
        return (self.get_single(k) for k in keys)

    def get_to_dict(self, *keys):
        return {k: self.get_single(k) for k in keys}

    def set_single(self, key, value, timeout=None):
        """Add a new key/value to the cache (overwrites value, if key already
        exists in the cache).
        :param key: the key to set
        :param value: the value for the key
        :param timeout: the cache timeout for the key in seconds (if not
                        specified, it uses the default timeout). A timeout of
                        0 idicates that the cache never expires.
        :returns: ``True`` if key has been updated, ``False`` for backend
                  errors. Pickling errors, however, will raise a subclass of
                  ``pickle.PickleError``.
        :rtype: boolean"""

        return True

    def set(self, **kwargs):
        symbol = True
        for key, value in kwargs.iteritems():
            if not self.set_single(key, value, timeout=None):
                symbol = False
        return symbol

    def delete_single(self, key):
        pass

    def delete(self, *keys):

        return all(self.delete_single(key) for key in keys)

    def has(self, key):
        return 'True if exist else False'

    def clear(self):
        return True


class DictCache_LRUTTL(BaseCacheClass):

    def __init__(self, capacity=250, Pickled=True, default_timeout=300):
        super(LRUDict, self).__init__()
        self.default_timeout = default_timeout
        self._capacity = capacity
        self.save_func = self.picklesave if Pickled else self.normalsave
        self.load_func = self.pickleload if Pickled else self.normalload

    def set_default_timeout(self, timeout):
        self.default_timeout = timeout if isinstance(
            timeout, (int, float)) else 300

    def __setitem__(self, key, value):
        containsKey = 1 if key in self else 0
        if len(self) - containsKey >= self._capacity:
            last = self.popitem(last=False)
            # print 'remove:', last
        if containsKey:
            del self[key]
            # print 'set:', (key, value)
        else:
            pass
            # print 'add:', (key, value)
        OrderedDict.__setitem__(self, key, value)

    def _normal_timeout(self, timeout):
        import time
        if isinstance(timeout, (int, float)):
            expire = time.time() + timeout if timeout != 0 else 0
        else:
            expire = time.time() + self.default_timeout

        return expire

    def _prune(self):

        tempiter = (key for key, (expire, value) in self._cache.iteritems(
        ) if expire != 0 and expire <= time.time())
        return [self._cache.pop(_, None) for _ in tempiter]


class LastUpdatedOrderedDict(OrderedDict):

    def __init__(self, capacity):
        super(LastUpdatedOrderedDict, self).__init__()
        self._capacity = capacity

    def __setitem__(self, key, value):
        containsKey = 1 if key in self else 0
        if len(self) - containsKey >= self._capacity:
            last = self.popitem(last=False)
            # print 'remove:', last
        if containsKey:
            del self[key]
            # print 'set:', (key, value)
        else:
            pass
            # print 'add:', (key, value)
        OrderedDict.__setitem__(self, key, value)


def Lcache(capacity=250):
    memo = LastUpdatedOrderedDict(capacity)

    def cache(func):
        @wraps(func)
        def _wrapper(*args):
            res = memo.get(args, None)
            if res is not None:
                return res
            else:
                res = func(*args)
                memo[args] = res
            return res

        return _wrapper

    return cache


if __name__ == '__main__':

    def fib(n):
        if n <= 1:
            return n
        else:
            return fib(n - 1) + fib(n - 2)


    print([fib(i) for i in list(range(31))])
