# -*- coding:utf-8 -*-
import sqlite3
import pandas as pd

class TransportDB(object):
    def __init__(self):
        pass

    def Transport(self,
                  DB1='RRnew.sqlite',
                  DB1columns=('UUID', 'Score', 'RelatedStock'),
                  DB1table='Industry',
                  DB2='RR.sqlite',
                  DB2table='ScoreRelatedStock'):

        print('Transport Start!')
        with sqlite3.connect(DB1) as conn1:
            df = pd.read_sql('select {} from {}'.format(','.join(DB1columns), DB1table), conn1)
        with sqlite3.connect(DB2) as conn2:
            import time
            df['CalculatedTime'] = round(time.time())
            df['TransportFrom'] = '{}.{}'.format(DB1, DB1table)
            df.to_sql(DB2table, conn2, if_exists='append', index=False)
        print('Transport Done!')
