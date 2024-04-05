# !/usr/bin/env python3
# coding=utf8
"""
omit
"""


import redis
from typing import Optional


class RedisHelperBase(object):
    """
    对 redis 包装了一层, 需要[pip install redis]
    """

    @classmethod
    def GET(cls, redis_object: redis.Redis, name) -> Optional[str]:
        """
        def get(self, name: KeyT) -> ResponseT:
        For more information see https://redis.io/commands/get
        代码文件: Python/Python310/site-packages/redis/commands/core.py
        key 存在, 返回 str
        key 不存在, 返回 None
        key 的 value 不是 string, 抛异常 redis.exceptions.ResponseError
        """
        dst = redis_object.get(name)
        dst = dst.decode(encoding='utf8') if isinstance(dst, bytes) else dst
        return dst

    @classmethod
    def SET(cls, redis_object: redis.Redis, name, value, ex=None):
        """
        def set(self, name: KeyT, value: EncodableT, ex: Union[ExpiryT, None] = None, px: Union[ExpiryT, None] = None, nx: bool = False, xx: bool = False, keepttl: bool = False, get: bool = False, exat: Union[AbsExpiryT, None] = None, pxat: Union[AbsExpiryT, None] = None,) -> ResponseT:
        For more information see https://redis.io/commands/set
        ex: 多少秒的过期时间
        返回值: 执行成功就返回 True
        发送之前, 会编码所有的参数, 比如 name 和 value, 它们接受 (str,bytes,memoryview,int,float), 如果是 (int,float) 就 [value = repr(value).encode()]
        例: value = 10086, GET 的结果是 b'10086'
        例: value = 1.618, GET 的结果是 b'1.618'
        Python/Python310/site-packages/redis/commands/core.py
        """
        return redis_object.set(name=name, value=value, ex=ex)

    @classmethod
    def DEL(cls, redis_object: redis.Redis, *names) -> int:
        """
        删除一个或多个name, 返回int, 删除个数, 如果不存在就返回0个
        def delete(self, *names: KeyT) -> ResponseT:
        不论 name 是 什么类型(string/hash/list/set/sorted_set)都可以删除
        """
        return redis_object.delete(*names)

    @classmethod
    def INCRBY(cls, redis_object: redis.Redis, name, amount: int = 1):
        """
        def incrby(self, name: KeyT, amount: int = 1) -> ResponseT:
        For more information see https://redis.io/commands/incrby
        返回值: 相加之后的值
        name 不存在就用零相加
        name 的 value 不是数字型 str 就抛异常 redis.exceptions.ResponseError
        """
        return redis_object.incrby(name, amount)

    @classmethod
    def DECRBY(cls, redis_object: redis.Redis, name, amount: int = 1):
        """
        def decrby(self, name: KeyT, amount: int = 1) -> ResponseT:
        For more information see https://redis.io/commands/decrby
        返回值: 相减之后的值
        name 不存在就用零相减
        name 的 value 不是数字型 str 就抛异常 redis.exceptions.ResponseError
        """
        return redis_object.decrby(name, amount)

    @classmethod
    def HGETALL(cls, redis_object: redis.Redis, name: str) -> dict:
        """
        def hgetall(self, name: str) -> Union[Awaitable[dict], dict]:
        For more information see https://redis.io/commands/hgetall
        返回值: dict
        name 不存在, 返回空的 dict
        name 的 value 不是 hash 就???
        """
        def b2s(src):
            return src.decode(encoding='utf8') if isinstance(src, bytes) else src

        dst = redis_object.hgetall(name)
        dst = {b2s(k): b2s(v) for k, v in dst.items()} if isinstance(dst, dict) else dst
        return dst

    @classmethod
    def HGET(cls, redis_object: redis.Redis, name: str, key: str):
        """
        def hget(self, name: str, key: str) -> Union[Awaitable[Optional[str]], Optional[str]]:
        For more information see https://redis.io/commands/hget
        返回值: 略
        name 不存在, 或, name 下面的 key 不存在, 返回 None
        """
        dst = redis_object.hget(name, key)
        dst = dst.decode(encoding='utf8') if isinstance(dst, bytes) else dst
        return dst

    @classmethod
    def HSET(cls, redis_object: redis.Redis, name: str, key: str = None, value: str = None, mapping: dict = None) -> int:
        """
        def hset(self, name: str, key: Optional[str] = None, value: Optional[str] = None, mapping: Optional[dict] = None, items: Optional[list] = None,) -> Union[Awaitable[int], int]:
        For more information see https://redis.io/commands/hset
        返回值: 为 name 新增几个 key 就返回几, 修改 name 的 key 不计数(不论修改成功与否),
        value 接受 (str,bytes,memoryview,int,float), 如果 value 是 (int,float) 就 [value = repr(value).encode()]
        示例:
        HSET(redis_object, 'test_hash_key', key='f1', value='v1')
        HSET(redis_object, 'test_hash_key', mapping={'f2': 2.71828, 'f3': 3, 'f4': 'v4'})
        """
        return redis_object.hset(name=name, key=key, value=value, mapping=mapping)

    @classmethod
    def HDEL(cls, redis_object: redis.Redis, name: str, *keys) -> int:
        """
        def hdel(self, name: str, *keys: List) -> Union[Awaitable[int], int]:
        For more information see https://redis.io/commands/hdel
        返回值: 为 name 删除几个 key 就返回几, name 不存在就返回 0,
        name 的 value 不是 hash 就抛异常 redis.exceptions.ResponseError
        示例:
        HSET(redis_object, 'test_hash_key', key='f1', value='v1')
        HSET(redis_object, 'test_hash_key', mapping={'f2': 2.71828, 'f3': 3, 'f4': 'v4'})
        HDEL(redis_object, 'test_hash_key', 'f1', 'f2', 'f3', 'f4')
        """
        return redis_object.hdel(name, *keys)

    @classmethod
    def LRANGE(cls, redis_object: redis.Redis, name: str, start: int, end: int) -> list:
        """
        def lrange(self, name: str, start: int, end: int) -> Union[Awaitable[list], list]:
        For more information see https://redis.io/commands/lrange
        返回值: 略
        name 不存在就返回空 list
        name 的 value 不是 list 就抛异常 redis.exceptions.ResponseError
        """
        def b2s(src):
            return src.decode(encoding='utf8') if isinstance(src, bytes) else src

        dst = redis_object.lrange(name, start, end)
        dst = [b2s(item) for item in dst] if isinstance(dst, list) else dst
        return dst

    @classmethod
    def RPUSH(cls, redis_object: redis.Redis, name: str, *values):
        """
        def rpush(self, name: str, *values: FieldT) -> Union[Awaitable[int], int]:
        For more information see https://redis.io/commands/rpush
        返回值: 插入之后, 列表有多少元素, 就返回几,
        name 不存在, 就新建一个空列表并执行 RPUSH 操作,
        name 的 value 不是 list 就抛异常 redis.exceptions.ResponseError
        """
        return redis_object.rpush(name, *values)

    @classmethod
    def LPUSH(cls, redis_object: redis.Redis, name: str, *values) -> int:
        """
        def lpush(self, name: str, *values: FieldT) -> Union[Awaitable[int], int]:
        For more information see https://redis.io/commands/lpush
        返回值: 插入之后, 列表有多少元素, 就返回几,
        name 不存在, 就新建一个空列表并执行 LPUSH 操作,
        name 的 value 不是 list 就抛异常 redis.exceptions.ResponseError
        将一个或多个值插入到列表头部
        例:
        RPUSH(redis_object, 'test_list_key', 'a1', 'a2')  =>             ['a1', 'a2']
        LPUSH(redis_object, 'test_list_key', 'b1', 'b2')  => ['b2', 'b1', 'a1', 'a2']
        """
        return redis_object.lpush(name, *values)

    @classmethod
    def LREM(cls, redis_object: redis.Redis, name: str, count: int, value: str) -> int:
        """
        def lrem(self, name: str, count: int, value: str) -> Union[Awaitable[int], int]:
        For more information see https://redis.io/commands/lrem
        返回值: 移除的元素个数
        count > 0: 从头到尾删除值为 value 的元素, 删除 count 个就停止,
        count < 0: 从尾到头删除值为 value 的元素, 删除 count 个就停止,
        count = 0: 删除所有的值为 value 的元素,
        """
        return redis_object.lrem(name, count, value)

    @classmethod
    def LINSERT(cls, redis_object: redis.Redis, name: str, where: str, refvalue: str, value: str):
        """
        def linsert(self, name: str, where: str, refvalue: str, value: str) -> Union[Awaitable[int], int]:
        For more information see https://redis.io/commands/linsert
        返回值: 插入之后, 列表有多少元素, 就返回几; 如果 refvalue 不在列表里, 就返回 -1,
        """
        return redis_object.linsert(name=name, where=where, refvalue=refvalue, value=value)

    @classmethod
    def redis_object(cls, _host, _port) -> redis.Redis:
        """"""
        _pool = redis.ConnectionPool(host=_host, port=_port, db=0)
        _conn = redis.StrictRedis(connection_pool=_pool)
        assert isinstance(_conn, redis.Redis)
        _conn: redis.Redis = _conn  # 标识一下类型
        return _conn


class RedisHelper(object):
    """"""

    def __init__(self) -> None:
        """"""
        self.redis: redis.client.Redis = None

    def initialize(self, host, port, *args, **kwargs):
        """"""
        assert self.redis is None
        self.redis = RedisHelperBase.redis_object(host, port)

    def GET(self, name):
        """"""
        return RedisHelperBase.GET(self.redis, name)

    def SET(self, name, value, ex=None):
        """"""
        return RedisHelperBase.SET(self.redis, name, value, ex)

    def DEL(self, *names) -> int:
        """"""
        return RedisHelperBase.DEL(self.redis, *names)

    def INCRBY(self, name, amount: int = 1):
        """"""
        return RedisHelperBase.INCRBY(self.redis, name, amount)

    def DECRBY(self, name, amount: int = 1):
        """"""
        return RedisHelperBase.DECRBY(self.redis, name, amount)

    def HGETALL(self, name: str) -> dict:
        """"""
        return RedisHelperBase.HGETALL(self.redis, name)

    def HGET(self, name: str, key: str):
        """"""
        return RedisHelperBase.HGET(self.redis, name, key)

    def HSET(self, name: str, key: str = None, value: str = None, mapping: dict = None) -> int:
        """"""
        return RedisHelperBase.HSET(self.redis, name=name, key=key, value=value, mapping=mapping)

    def HDEL(self, name: str, *keys) -> int:
        """"""
        return RedisHelperBase.HDEL(self.redis, name, *keys)

    def LRANGE(self, name: str, start: int, end: int) -> list:
        """"""
        return RedisHelperBase.LRANGE(self.redis, name=name, start=start, end=end)

    def RPUSH(self, name: str, *values):
        """"""
        return RedisHelperBase.RPUSH(self.redis, name, *values)

    def LPUSH(self, name: str, *values) -> int:
        """"""
        return RedisHelperBase.LPUSH(self.redis, name, *values)

    def LREM(self, name: str, count: int, value: str) -> int:
        """"""
        return RedisHelperBase.LREM(self.redis, name=name, count=count, value=value)

    def LINSERT(self, name: str, where: str, refvalue: str, value: str):
        """"""
        return RedisHelperBase.LINSERT(self.redis, name=name, where=where, refvalue=refvalue, value=value)


if __name__ == "__main__":
    # TODO: Redis 打日志,
    host = 'localhost'
    port = 8379

    redis_obj = RedisHelper()
    redis_obj.initialize(host, port)

    try:
        ret = redis_obj.SET('test_str_key', '3')
        print(type(ret), ret)
        ret = redis_obj.INCRBY('test_str_key', 7)
        print(type(ret), ret)
    except redis.exceptions.ResponseError as ex:
        print(type(ex), ex)
    pass
