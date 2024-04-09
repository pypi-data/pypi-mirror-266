# coding=utf-8
"""this file is to create the general connection for mysql or mariadb.

provide a basic function and enforence function for some reasons
"""

import pandas as pd
import pymysql
import sqlalchemy

from collections import namedtuple


class BaseMysql(object):
    """
    It is the base class for mysql connection.

    also, to provide a way to create connector and engine via sqlachemy
    """

    def __init__(self,
                 mysql_name,
                 host='localhost',
                 port=3306,
                 user='web',
                 passwd='Imweb',
                 charset='UTF8',
                 db='com_stable'):
        """
        initialization for class!
        :param mysql_name:
        :param host:
        :param port:
        :param user:
        :param passwd:
        :param charset:
        :param db:
        """

        SQLConnector = namedtuple(mysql_name, ['host',
                                               'port',
                                               'user',
                                               'passwd',
                                               'charset',
                                               'db'])
        self._para = SQLConnector(host, port, user, passwd, charset, db)

    def _SelfConnect(self):
        """
        create the connector for the mysql sql command.
        :param self:
        :return:
        """

        return pymysql.connect(host=self._para.host,
                               port=self._para.port,
                               user=self._para.user,
                               passwd=self._para.passwd,
                               charset=self._para.charset,
                               db=self._para.db)

    def _SelfEngine(self):
        """
        create the cursor for the mysql sql command.
        :return:
        """
        engine_str = 'mysql+pymysql://{}:{}@{}:{}/{}?charset={}'

        # use sqlalchemy to create engine

        return sqlalchemy.create_engine(engine_str.format(self._para.user,
                                                          self._para.passwd,
                                                          self._para.host,
                                                          self._para.port,
                                                          self._para.db,
                                                          self._para.charset))


class ConnectMysql(BaseMysql):
    """

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sql2data(self, sql):
        """
        this is the function to get data from sql queries and
        transform the data into the dataframe via pandas
        :param sql:
        :return:
        """
        # type: (str) -> dataframe

        conn = self.SelfConnect()
        df = pd.read_sql(sql, conn)
        conn.close()
        return df

    def DetectConnectStatus(self, returnresult=True, printout=False):
        """
        detect function for connect the mysql server and return useful information to response the expect messages.

        :param returnresult:
        :param printout:
        :return:
        """

        try:
            result = self.Excutesql()
            status = 'Good connection!'
            if printout:
                print(status)
        except pymysql.OperationalError as e:
            result = str(e)
            status = 'Bad connection!'
            if printout:
                print(e)
        finally:
            if returnresult:
                return result
            else:
                return status

    def Excutesql(self, sql='SHOW DATABASES'):
        """
        execute the sql command for the any reasonable sql commands and queries

        :param sql:
        :return:
        """

        conn = self._SelfConnect()
        cur = conn.cursor()

        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        conn.commit()
        conn.close()
        return result

    def SHOWDATABASES(self):
        """
        simple command for showing all databases。


        :return:
        """
        return self.Excutesql(sql='SHOW DATABASES')

    def SHOWTABLES(self):
        """
        simple command for  showing all tables under current datavases
        under given the connector parameters.
        :return:
        """
        return self.Excutesql(sql='SHOW TABLES')


if __name__ == '__main__':
    pass
