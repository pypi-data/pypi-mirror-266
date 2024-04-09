# -*- coding:utf-8 -*-
import pandas as pd
import pymysql
import sqlalchemy
import sqlite3


class ConnectMysql(object):
    # C_RR_ResearchReport
    def __init__(self, MysqlName, host='192.168.0.210', port=3306, user='develop', passwd='sd61131707', charset='UTF8',
                 db='com_stable'):
        # super(LRUDict_UnPickled, self).__init__()
        from collections import namedtuple
        SQLConnector = namedtuple(MysqlName, ['host', 'port', 'user', 'passwd', 'charset', 'db'])
        self.para = SQLConnector(host, port, user, passwd, charset, db)

    def sql2data(self, sql):
        # type: (str) -> dataframe
        conn = self.SelfConnect()
        df = pd.read_sql(sql, conn)
        conn.close()
        return df

    def DetectConnectStatus(self, returnresult=True, printout=False):

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

    def SelfConnect(self):
        conn = pymysql.connect(host=self.para.host, port=self.para.port, user=self.para.user, passwd=self.para.passwd,
                               charset=self.para.charset, db=self.para.db)
        return conn

    def SelfEngine(self):
        engine = sqlalchemy.create_engine(
            'mysql+pymysql://{}:{}@{}:{}/{}?charset={}'.format(self.para.user, self.para.passwd, self.para.host,
                                                               self.para.port, self.para.db,
                                                               self.para.charset))  # 用sqlalchemy创建引擎
        # print(engine)
        return engine

    def DF2mysql(self, df, tablename, engine='SelfEngine', if_exists='replace', index=False):
        if isinstance(engine, str) and engine == 'SelfEngine':
            df.to_sql(tablename, con=self.SelfEngine(), if_exists=if_exists, index=index)
        else:
            df.to_sql(tablename, con=engine, if_exists=if_exists, index=index)

    def Excutesql(self, sql='SHOW DATABASES'):
        conn = self.SelfConnect()
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result

    def SHOWDATABASES(self):
        return self.Excutesql()

    def SHOWTABLES(self):
        return self.Excutesql(sql='SHOW TABLES')

    def TransportResult(self, transported):
        if len(transported) == 0:
            print('Nothing has been transported from sqlite to mysql')
        elif len(transported) == 1:
            print('{}  has been transported from sqlite to mysql'.format(transported[0]))
        else:
            print("{} have been transported from sqlite to mysql".format(','.join(transported)))

    def Sqlite2MysqlAll(self, sqlitefile, if_exists='replace', index=False):
        transported = []
        with sqlite3.connect(sqlitefile) as conn:
            tables = pd.read_sql('select tbl_name from sqlite_master where type="table"  ', conn)
            if not tables.empty:
                for table in tables.values.ravel():
                    sql = 'select * from {}  '.format(table)
                    self.DF2mysql(pd.read_sql(sql, conn), table, engine='SelfEngine', if_exists=if_exists, index=index)
                    transported.append(table)
            else:
                print('Empty DataFrame from Sqlite!!!')
                print('Sequence Done Because of empty DataFrame')
        self.TransportResult(transported)

    def Sqlite2MysqlSingleSameTable(self, sqlitefile, sqlitetable, if_exists='replace', index=False):
        transported = []
        with sqlite3.connect(sqlitefile) as conn:
            try:
                sql = 'select * from {}  '.format(sqlitetable)
                self.DF2mysql(pd.read_sql(sql, conn), sqlitetable, engine='SelfEngine', if_exists=if_exists,
                              index=index)
                transported.append(sqlitetable)
            except (pd.io.sql.DatabaseError, sqlite3.DatabaseError) as e:
                print(e)
                print('Accidentally exit! SQL Command Unexecuted')
            else:
                print('Specially Write SQL Completed')
        self.TransportResult(transported)

    def Sqlite2Mysql(self, sqlitefile, sqlitetable='All', mysqltable='SameTable', method='SameTable',
                     if_exists='replace', index=False):
        import sqlite3
        if method == 'SameTable':
            if isinstance(sqlitetable, str):
                if sqlitetable == 'All':
                    # collect tables
                    self.Sqlite2MysqlAll(sqlitefile, if_exists=if_exists, index=index)
                else:
                    # input special dateframe
                    self.Sqlite2MysqlSingleSameTable(sqlitefile, sqlitetable, if_exists='replace', index=False)
            else:
                raise ValueError(
                    'sqlitetable obtain unsupported type input. sqlitetable only support str but obtain: {}'.format(
                        type(sqlitetable)))
        elif method == 'OtherTable' and isinstance(mysqltable, str):
            if isinstance(mysqltable, dict):
                with sqlite3.connect(sqlitefile) as conn:
                    tables = pd.read_sql('select tbl_name from sqlite_master where type="table"  ', conn)
                    transported = []
                    for key in mysqltable.keys():
                        if key in tables.values.ravel():
                            sql = 'select * from {}  '.format(key)
                            self.DF2mysql(pd.read_sql(sql, conn), mysqltable[key], engine='SelfEngine',
                                          if_exists=if_exists,
                                          index=index)
                            transported.append(key)
                        else:
                            pass

                    self.TransportResult(transported)

            else:
                raise ValueError(
                    "Unexpect parameter: mysqltable with value {}. Dict required but get: {} ".format(mysqltable,
                                                                                                      type(mysqltable)))

    def getRRviaDB(self, name, table, limit=30, db=None, filtername=None):
        # type: (str, str, int, str) -> DataFrame

        db = self.para.db if db is None else db
        if name == 'ALL':
            if isinstance(limit, int):
                sql = """
                        SELECT *
                        FROM `%s`.`%s`
                        LIMIT 0 , %d
                        """ % (db, table, limit)
            else:
                sql = """
                        SELECT *
                        FROM `%s`.`%s`
                        """ % (db, table)
        else:
            if isinstance(limit, int):
                sql = """
                        SELECT *
                        FROM `%s`.`%s`
                        WHERE `%s` = '%s'
                        LIMIT 0 , %d
                        """ % (db, table, filtername, name, limit)
            else:
                sql = """
                        SELECT *
                        FROM `%s`.`%s`
                        WHERE `%s` = '%s'
                        """ % (db, table, filtername, name)

        return self.sql2data(sql)


if __name__ == '__main__':
    pass
