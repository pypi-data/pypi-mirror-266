# coding=utf8

import redis
import sqlite3
import pandas as pd


class RedisList(object):
    def __init__(self, redis_instance):
        self.redis_instance = redis_instance

    def create(self, list_name, *values):
        """

        :param list_name:
        :param values:
        :return:
        """
        self.redis_instance.lpush(list_name, *values)

    def add(self, list_name, *values):
        """

        :param list_name:
        :param values:
        :return:
        """
        self.redis_instance.lpush(list_name, *values)

    def pop(self, list_name, method='blpop'):
        """

        :param list_name:
        :param method:
        :return:
        """
        return getattr(self.redis_instance, method)(list_name)

    def length(self, list_name):
        """

        :param list_name:
        :return:
        """
        return self.redis_instance.llen(list_name)


class RedisController(object):
    """
    this is class for manage a cluster of redis
    """
    def __init__(self, host, port, password, db=0):
        self._redis_instance = RedisConnector(host=host, port=port, password=password, db=db)

        self.RedisList = RedisList(self._redis_instance)


class RedisConnector(redis.Redis):
    def __init__(self, host, port, password, db=0):
        # self.redis = redis.Redis.from_url('redis://{}@{}:{}/{}'.format(password, host, port, db))
        super(RedisConnector, self).__init__(host=host, port=port, password=password, db=db)
        # self.r = redis.Redis()

    def execute(self, cmd, *key):
        """
        general function for redis query
        :param cmd:
        :param key:
        :return:
        """
        return getattr(self, cmd)(*key)

    def _create_list(self, list_name, *values):
        """

        :param list_name:
        :param values:
        :return:
        """
        self.lpush(list_name, *values)

    def add_value_into_list(self, list_name, *values):
        """

        :param list_name:
        :param values:
        :return:
        """
        self._create_list(list_name, *values)

    def obtain_a_task_once(self, redis_key):
        """

        :param redis_key:
        :return:
        """
        return self.lpop(redis_key)

    def obtain_a_task_else_waiting(self, redis_key, timeout=10):
        """

        :param redis_key:
        :param timeout:
        :return:
        """
        return self.blpop(redis_key, timeout)

    @staticmethod
    def byte2str(b):
        """

        :param b:
        :return:
        """
        return b.decode('utf8') if isinstance(b, bytes) else b


if __name__ == '__main__':
    # tasks_df = load_task()
    rr = RedisConnector()
    # rr._create_list('LagouTaskstest', *tasks_df.values.ravel())
    rr.add_value_into_list('b', 1)
    retu = rr.obtain_a_task_else_waiting('b', 1)
    print(retu, retu is not None)
    # print(type(retu), type(retu.decode('utf8')))
    print(isinstance(retu, bytes))
