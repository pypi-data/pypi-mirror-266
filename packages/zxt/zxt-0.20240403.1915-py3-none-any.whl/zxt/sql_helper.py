# !/usr/bin/env python3
# coding=utf8
"""
一些"代码分析工具"(比如 Pylint)能检出不符合编码风格标准和有潜在风险的代码。
由于 python 2 和 python 3 部分语法不同，"代码分析工具"会识别 .py 文件头部的解释器来判断该文件 python 版本。
如果发现 python 3 文件报出了 invalid syntax 错误，可能是由于被当成了 python 2 扫描。
此时在文件首行加上右面的代码即可：# !/usr/bin/env python3

定义编码【# coding=<encoding name>】参见: http://www.python.org/peps/pep-0263.html

对 SQL 的简单封装，支持 MySQL 和 SQLite
"""


import json
import pathlib
import peewee
import playhouse.db_url
import pymysql
import pymysql.cursors
import sqlite3
import threading
from typing import Dict, List, Tuple, Optional, Union


class SqlHelper(object):
    """
    使用示例:
    url: str = "sqlite:///:memory:"
    url: str = "mysql://用户:密码@主机:端口/数据库?charset=字符集"
    url: str = "mysql://root:toor@localhost:13306/mysql?charset=utf8"
    sqlhelper = SqlHelper()
    sqlhelper.initialize(url=url, lazy_init=True)
    results: list = sqlhelper.select("SELECT 3*7 AS number;", isDictNotList=True)
    print(results)
    sqlhelper.execute("CREATE TEMPORARY TABLE temp_test(kkk VARCHAR(256) NOT NULL, vvv VARCHAR(512) NOT NULL);")
    sqlhelper.execute("INSERT INTO temp_test(kkk,vvv)VALUES('k1','v1'),('k2','v2');")
    results: list = sqlhelper.select("SELECT * FROM temp_test;", isDictNotList=True)
    print(results)
    sqlhelper.terminate()

    lazy_init: 延迟初始化数据库连接, 真正要执行 SQL 语句的时候, 才开始连接到数据库,
    只有指定的机器可以连接到对应的线上数据库, 多个线上库可能指定了不同的机器,
    可能会出现: 机器 A 能连接数据库 1 和 数据库 2, 机器 B 能连接数据库 2 和 数据库 3,
    我有一个数据库配置文件, 配置了所有的数据库连接参数, 一旦加载这个配置文件, 就会因为无法连接数据库导致程序报错,
    遂添加 lazy_init 参数,
    """
    # python peewee模块执行原生sql语句的方法
    # https://www.cnblogs.com/renfanzi/p/13469860.html

    def __init__(self, *args, **kwargs) -> None:
        """"""
        self.lock = threading.Lock()
        self.url: str = ""
        self.lazy_init: bool = False  # 延迟初始化数据库,
        self.connection: Union[peewee.MySQLDatabase, peewee.SqliteDatabase, None] = None
        self.cursor: Union[pymysql.cursors.Cursor, sqlite3.Cursor, None] = None

    def initialize(self, url: str, lazy_init: bool = False, *args, **kwargs) -> None:
        """"""
        self.url: str = url
        self.lazy_init: bool = lazy_init

        if not self.lazy_init:
            self._lazy_initialize_db()

    def _lazy_initialize_db(self) -> None:
        """"""
        for _ in range(1):
            # 无需加锁, 判断有值, 立即返回,
            if self.connection:
                break

            with self.lock:
                # 判断有值, 立即返回, 无需重复初始化,
                if self.connection:
                    break

                self.connection: Union[peewee.MySQLDatabase, peewee.SqliteDatabase] = playhouse.db_url.connect(url=self.url)  # noqa E501
                self.cursor = self.connection.cursor()  # 若此处抛异常, 通常是拒绝连接/拒绝访问等原因,
        pass

    def terminate(self) -> None:
        """"""
        for _ in range(1):
            if not self.connection:
                break

            with self.lock:  # self.lock.acquire(); self.lock.release();
                if not self.connection:
                    break

                self.cursor.close()
                self.cursor = None
                self.connection.close()
                self.connection = None

    def __del__(self) -> None:
        """"""
        self.terminate()

    def select(self, sql: str, params: Union[list, tuple, dict, None] = None, isDictNotList: bool = False) -> List[Union[tuple, dict]]:
        """
        sqlite: 不具名占位符{?} 具名占位符{:name}
        mysql : 不具名占位符{%s}具名占位符{%(name)s}
        sqlhelper.select("SELECT 'sqlite'AS tag, ?        * ?       AS total", (3, 7), True)
        sqlhelper.select("SELECT 'sqlite'AS tag, :unit    * :num    AS total", {"unit": 3, "num": 7}, True)
        sqlhelper.select("SELECT 'mysql' AS tag, %s       * %s      AS total", (3, 7), True)
        sqlhelper.select("SELECT 'mysql' AS tag, %(unit)s * %(num)s AS total", {"unit": 3, "num": 7}, True)
        """
        self._lazy_initialize_db()

        if params is None:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, params)

        results = self.fetchall(cursor=self.cursor, isDictNotList=isDictNotList)

        return results

    def commit(self) -> None:
        """"""
        self._lazy_initialize_db()

        self.connection.commit()

    def rollback(self) -> None:
        """"""
        self._lazy_initialize_db()

        self.connection.rollback()

    def execute(self, sql: str, params: Union[list, tuple, dict, None] = None, commit: bool = True) -> None:
        """
        * sqlite: question marks (qmark style) or named placeholders (named style)
        https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.execute
        https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders
        An SQL statement may use one of two kinds of placeholders:
        question marks (qmark style) or named placeholders (named style).
        * mysql : variables using %s or %(name)s parameter style
        https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html
        The parameters found in the tuple or dictionary params are bound to the variables in the operation.
        Specify variables using %s or %(name)s parameter style (that is, using format or pyformat style).
        """
        self._lazy_initialize_db()

        if params is None:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, params)

        if commit:
            self.commit()

    @classmethod
    def fetchall(cls, cursor: Union[pymysql.cursors.Cursor, sqlite3.Cursor], isDictNotList: bool = False) -> List[Union[tuple, dict]]:
        """如果结果是空,且(isDictNotList=True),那么结果为空,不利于保存到文件"""
        if isDictNotList:
            head = [col[0] for col in cursor.description]
            results = [dict(zip(head, data)) for data in cursor.fetchall()]
        else:
            head = [col[0] for col in cursor.description]
            results = [data for data in cursor.fetchall()]
            results.insert(0, head)
        return results

    @classmethod
    def fetchone(cls, cursor: Union[pymysql.cursors.Cursor, sqlite3.Cursor], isDictNotList: bool = False) -> List[Union[tuple, dict]]:
        """如果结果是空,且(isDictNotList=True),那么结果为空,不利于保存到文件"""
        if isDictNotList:
            head = [col[0] for col in cursor.description]
            results = [dict(zip(head, data)) for data in (cursor.fetchone(),)]
        else:
            head = [col[0] for col in cursor.description]
            results = [data for data in (cursor.fetchone(),)]
            results.insert(0, head)
        return results


class SqlHelperSet(object):
    """"""

    def __init__(self, *args, **kwargs):
        """"""
        self._connections: Dict[str, SqlHelper] = {}

    def initialize(self, conf: Union[str, dict], *args, **kwargs):
        """"""
        if isinstance(conf, (str, pathlib.Path)):  # 文件路径,
            with open(file=conf, mode="r", encoding="utf8") as fp:
                conf_obj = json.load(fp=fp)
        else:
            conf_obj = conf  # 文件内容,

        for name, params in conf_obj.items():
            assert isinstance(name, str) and (name != '')  # name 不可为空
            assert isinstance(params, dict)

            sql_helper = SqlHelper()
            sql_helper.initialize(**params)
            self._connections[name] = sql_helper

        pass

    def terminate(self):
        """"""
        if not self._connections:
            return

        for _, connection in self._connections.items():
            connection.terminate()

        self._connections.clear()

    def __del__(self):
        """"""
        self.terminate()

    def _get_connection(self, name: str) -> Optional[SqlHelper]:
        """"""
        connection: Optional[SqlHelper] = None

        # 如果只有一个连接, 查询时又没有指定连接的名字, 那么就使用这唯一的一个连接,
        if not name and isinstance(self._connections, dict) and len(self._connections) == 1:
            connection = self._connections.values().__iter__().__next__()
        else:
            connection = self._connections.get(name, None)

        return connection

    def select(self, sql: str, params: Union[list, tuple, dict, None] = None, isDictNotList: bool = False, name: str = None) -> list:
        """"""
        connection: Optional[SqlHelper] = self._get_connection(name)
        return connection.select(sql=sql, params=params, isDictNotList=isDictNotList)


if __name__ == '__main__':
    conf_obj = {
        "testdb": {
            "url": "mysql://root:toor@localhost:13306/mysql?charset=utf8",
            "lazy_init": True,
            "__note": "测试环境的MySQL",
        },
        "memory": {
            "url": "sqlite:///:memory:",
            "lazy_init": True,
            "__note": "内存模式的SQLite",
        }
    }
    shs = SqlHelperSet()
    shs.initialize(conf=conf_obj)

    sql_statement = 'SELECT 3*7 AS number;'
    results = shs.select(sql_statement, isDictNotList=True, name="memory")
    print(results)

    sqlhelper = shs._get_connection(name="memory")
    results = sqlhelper.select("SELECT 'sqlite'AS tag, :unit    * :num    AS total", {"unit": 3, "num": 7}, True)
    print(results)
    del sqlhelper

    shs.terminate()
