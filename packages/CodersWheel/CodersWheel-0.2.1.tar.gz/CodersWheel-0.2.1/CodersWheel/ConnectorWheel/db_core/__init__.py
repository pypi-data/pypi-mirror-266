# coding=utf8



class DB(object):
    @staticmethod
    def DB(db_type, **kwargs):
        if db_type == 'redis':
            from Redisconnector import RedisConnector
            return RedisConnector(**kwargs)
        elif db_type == 'mysql':
            from MysqlConnector import ConnectMysql
            return ConnectMysql(**kwargs)


if __name__ == '__main__':
    pass
