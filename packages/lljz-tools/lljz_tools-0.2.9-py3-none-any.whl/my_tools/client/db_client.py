# coding=utf-8

"""
@fileName       :   db_client.py
@data           :   2024/2/8
@author         :   jiangmenggui@hosonsoft.com
"""
import re

import pymysql
from dbutils.pooled_db import PooledDB
from pymysql.cursors import DictCursor

from my_tools.attribute_dict import AttributeDict
from my_tools.decorators import singleton


class DBConnection(AttributeDict, total=True, variable=False, check_type=True):
    host: str
    port: int
    database: str
    user: str = ''
    password: str = ''


class _MySQLContext:

    def __init__(self, con):
        self.con = con
        self.cur = self.con.cursor(DictCursor)
        self.cur.commit = self.con.commit
        self.cur.rollback = self.con.rollback

    def close(self):
        self.cur.close()
        self.con.close()

    def commit(self):
        self.con.commit()

    def rollback(self):
        self.con.rollback()

    def select_one(self, sql, params=None):
        self.cur.execute(sql, params)
        return self.cur.fetchone()

    def select_many(self, sql, params=None, size: int = None):
        count = self.cur.execute(sql, params)
        if size is None:
            if count <= 10_000:
                return self.cur.fetchall()
            raise ValueError('查询结果过多(>10w),，请指定many参数')
        return self.cur.fetchmany(size)

    def select_all(self, sql, params=None):
        return self.select_many(sql, params, None)

    def execute(self, sql, params=None):
        return self.cur.execute(sql, params)

    def executemany(self, sql, params):
        return self.cur.executemany(sql, params)

    def dml(self, sql: str, params=None, limit: int | None = 1000):
        t, *_ = sql.lstrip().split(maxsplit=1)
        if t.upper() not in ('INSERT', 'UPDATE', 'DELETE'):
            raise ValueError(f'DML操作不支持{t}语句')
        if params:
            params = tuple(params)
            if isinstance(params[0], tuple | set | list):
                count = self.executemany(sql, params)
            else:
                count = self.execute(sql, params)
        else:
            count = self.execute(sql)
        if limit and t.upper() != 'INSERT' and count > limit:
            self.rollback()
            raise ValueError(f'影响行数超过{limit}行')
        return count

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start_transaction(self):
        return _TransactionManger(self.con)


@singleton('uri')
class DBClientPool:

    def __init__(self, uri: str, mincached=1, maxcached=5,
                 maxshared=5, maxconnections=100, blocking=False,
                 maxusage=None):
        """
        数据库连接
        :param uri: 连接串，格式如：mysql://user:password@host:port/database
        :param mincached: 连接池中空闲连接的初始数量
        :param maxcached: 连接池中空闲连接的最大数量
        :param maxshared: 共享连接的最大数量
        :param maxconnections: 创建连接池的最大数量
        :param blocking: 超过最大连接数量时候的表现，为True等待连接数量下降，为False直接报错处理
        :param maxusage: 单个连接的最大重复使用次数
        """
        obj = re.match(
            r'^mysql://(?P<user>.+):(?P<password>.+)@(?P<host>.+):(?P<port>\d+)/(?P<database>.+)$',
            uri
        )
        if not obj:
            raise ValueError('uri is wrong!')
        self.connection = DBConnection(obj.groupdict())
        self._pool = PooledDB(
            creator=pymysql,
            mincached=mincached,
            maxcached=maxcached,
            maxshared=maxshared,
            maxconnections=maxconnections,
            blocking=blocking,
            maxusage=maxusage,
            **self.connection
        )

    def connect(self) -> _MySQLContext:
        return _MySQLContext(self._pool.connection())

    def close(self):
        self._pool.close()


class _TransactionManger:

    def __init__(self, con):
        self.con = con

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.commit()


if __name__ == '__main__':
    # with MySQLClient('mysql://root:myroot123!@127.0.0.1:3306/server_monitor').connect() as client:
    #     client.execute('select * from information_schema.TABLES where TABLE_SCHEMA=%s', ['server_monitor'])
    #     print(client.fetchall())
    p1 = DBClientPool('mysql://root:Hosonsoft2020@192.168.1.220:3307/riin-platform')
    p2 = DBClientPool('mysql://root:Hosonsoft2020@192.168.1.220:3307/riin-platform')
    print(p1 is p2)
    with DBClientPool('mysql://root:Hosonsoft2020@192.168.1.220:3307/riin-platform').connect() as client:
        print(client.select_one("SELECT COUNT(*) FROM om_customer_order where id = %s", [1]))
        with client.start_transaction():
            client.dml("update om_customer_order set node_code = %s where id = %s", ['0701', 1])
