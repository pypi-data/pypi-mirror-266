# -*- coding: utf-8 -*-
# # Copyright by sn0wfree 2018
# ----------------------------
import pandas as pd
import sqlite3

def QuickConnectSqlite2DF(sql,sqlitename):
    import sqlite3
    with sqlite3.connect(sqlitename) as conn:
        df=pd.read_sql(sql,conn)
    return df


class SqliteDB(object):

    def __init__(self, DBpara, memory=True):
        self.conn = self.CreateDB(DBpara, memory)
        # self.cursor = self.conn.cursor()

    def CreateDB(self, DBpara, memory=True):
        if memory is True:
            DBname = ':memory:'
        elif isinstance(DBpara, str):
            DBname = DBpara
        elif isinstance(DBpara, dict):
            dbname = DBpara.get('DBname')
            DBname = dbname if dbname is not None else ':memory:'
        else:
            print('Unexpected DBpara: {}. will turn to in memory sqlite'.format(DBpara))
            DBname = ':memory:'

        return sqlite3.connect(DBname)

    def Search(self, sql, method='pandas'):
        if method == 'pandas':
            return self.SearchbyPANDAS(sql)
        else:
            return self.SearchbySQL(sql, method=method)

    def SearchbySQL(self, sql, method='SQL-cursor'):
        if method == 'SQL-cursor':
            return self.conn.cursor().execute(sql).fetchall()
        elif method == 'SQL-conn':
            return self.conn.execute(sql)
        else:
            return self.conn.cursor().execute(sql).fetchall()

    def SearchbyPANDAS(self, sql):
        return pd.read_sql(sql, self.conn)


class inMemoryDB(object):

    def __init__(self, DBpara=':memory:', DBype='sqlite', memory=True):
        import sqlite3
        self.DB = self.CreateDB(DBpara, DBype, memory)
        self.conn = self.DB.conn
        self.memory = True

    def CreateDB(self, DBpara, DBype='sqlite', memory=True):
        if DBype == 'sqlite':

            return self.CreateSQLiteDB(DBpara, memory=memory)
        else:
            print('currently cannot support other databse will turn to sqlite')
            return self.CreateSQLiteDB(DBpara, memory=memory)

    def CreateSQLiteDB(self, DBpara, memory):
        return SqliteDB(DBpara, memory)

    def Search(self, sql, method='pandas'):
        return self.DB.Search(sql, method)


class DBPool(inMemoryDB):

    def __init__(self, DBpara=':memory:', DBype='sqlite', memory=True):
        super(DBPool, self).__init__(DBpara, DBype, memory)


if __name__ == '__main__':
    pass
