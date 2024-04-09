# coding=utf8
import asyncio
import aiomysql, warnings
import time, random, gevent
from functools import reduce
import pandas as pd


# @asyncio.coroutine
# def test_example(loop):
#     conn = yield from aiomysql.connect(host='112.74.189.154', port=3306,
#                                        user='linlu', password='Imsn0wfree', db='mysql',
#                                        loop=loop)
#
#     cur = yield from conn.cursor()
#     yield from cur.execute("SELECT Host,User FROM user")
#     print(cur.description)
#     (r,) = yield from cur.fetchall()
#     print(r)
#     yield from cur.close()
#     conn.close()
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(test_example(loop))


class AsyncMysql(object):
    @staticmethod
    def chunks(l, chunksize, raise_error=True, critical_level=500):
        """Yield successive n-sized chunks from l."""
        # print(len(l)/ chunksize)
        if raise_error and len(l) / chunksize >= critical_level:
            raise ValueError('chunksize is too small or taskspool is too bigger!')
        elif raise_error is False and len(l) / chunksize >= critical_level:
            import math
            chunksize = math.ceil(len(l) / critical_level)
        else:
            pass

        for i in range(0, len(l), chunksize):
            yield l[i:i + chunksize]

    @staticmethod
    async def async_for(iterablelist):
        for sql in iterablelist:
            await asyncio.sleep(1)
            yield sql

    @staticmethod
    async def test_cursor_execute_func(pool, sql):
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # async for sql_result in cur_execute(cur, sql_set):
                #     holder.append(sql_result)

                await cur.execute(sql)
                sql_result = await cur.fetchall()
                col = list(map(lambda x: x[0], cur.description))
                # print(time.time(), sql_result)
                return sql, col, sql_result

    @classmethod
    async def cur_execute(cls, loop, mysqlpara, sqlset):
        pool = await aiomysql.create_pool(**mysqlpara, loop=loop)
        holder = [await cls.test_cursor_execute_func(pool, sql) for sql in sqlset]
        # holder = [await  test_example(pool, sql) async for sql in async_for(sqlset)]

        pool.close()
        await pool.wait_closed()
        return holder

    @staticmethod
    def parse_result(res, to_df=False, merge=False):
        from itertools import chain
        res = chain(*list(map(lambda x: x._result, res[0])))
        if to_df:
            res = ((sql, col, pd.DataFrame(list(data), columns=col)) for sql, col, data in res)
            # res : (sql, col, data)
            if merge:
                return pd.concat(map(lambda x: x[-1], res))
            else:
                return res
        else:
            if merge:
                warnings.warn('to_df is False, switch merge to False forced!')
            return list(res)

    # assert r == 42
    @classmethod
    def main_query(cls, mysqlpara, sqlset, chunksize=100, to_df=False, merge=False):
        """
        the main function of query executing function with async coroutine version

        :param mysqlpara:  mysql parameter
        :param sqlset:  a set or a list of sql
        :param chunksize:  chunk size of group
        :param to_df:  whether to dataframe
        :param merge:  whether merge
        :return: a tuple of data
        """
        loop = asyncio.get_event_loop()
        # [cur_execute(loop, mysqlpara,sql)  for sql in chunks(sqlset,5) ]

        # s = loop.run_until_complete(asyncio.wait([cur_execute(loop, mysqlpara, sqlset),
        #                                           cur_execute(loop, mysqlpara, sqlset10),
        #                                           cur_execute(loop, mysqlpara, sqlset20)]))

        s = loop.run_until_complete(
            asyncio.wait([cls.cur_execute(loop, mysqlpara, sql) for sql in cls.chunks(sqlset, chunksize)]))

        res = cls.parse_result(s, to_df=to_df, merge=merge)
        loop.close()
        return res

    @classmethod
    def mysql_conn_main_query(cls, MysqlConn_V004, sqlset, chunksize=100, to_df=False, merge=False):
        mysqlpara = MysqlConn_V004._para
        return cls.main_query(cls, mysqlpara, sqlset, chunksize=chunksize, to_df=to_df, merge=merge)


if __name__ == '__main__':


    print(1)
