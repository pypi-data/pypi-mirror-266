# !/usr/bin/env python3
# coding=utf8
""""""
import itertools
import numba


# @numba.jit(nopython=True)  # Just-in-time compilation (即时编译)
def ess(n):
    """
    求2到n范围内所有素数
    https://zhuanlan.zhihu.com/p/400818808
    """
    es = [2]
    Td = [True] * (n + 1)
    for i in range(3, n + 1, 2):
        if Td[i]:
            es.append(i)
            for j in range(i ** 2, n + 1, 2 * i):
                Td[j] = False
    return es


def chunk(ary, size: int, is_iter: bool = False):
    """
    同 PHP 的 array_chunk
    例如: chunk(range(1, 15), 3)
    https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
    """
    _arr = iter(ary)
    _itr = iter(lambda: tuple(itertools.islice(_arr, size)), ())
    return _itr if is_iter else list(_itr)


def array_split(ary, count: int) -> list:
    """
    将 ary 里的数据尽量均分成 count 份
    例如: array_split(list(range(1, 15)), 3)
    效果类似于 numpy.array_split(range(1,15), 3)
    """
    nums = [int(len(ary) / count) for _ in range(count)]
    for i in range(len(ary) - int(len(ary) / count) * count):  # 还剩这些数据尚未分配
        nums[i] += 1
    pairs = [(sum(nums[0:i]), nums[i]) for i in range(count)]
    parts = [ary[begin: begin + num] for begin, num in pairs]
    return parts


def list_chunk(_src: list, size: int) -> list:
    """
    直接在 python 命令行执行下面的语句, 多按两次回车, 会得到 list_chunk 函数, 它和 php 的 array_chunk 神似,
    def list_chunk(_src, size): return [_src[i:i + size] for i in range(0, len(_src), size)]
    """
    _dst: list = [_src[i:i + size] for i in range(0, len(_src), size)]
    return _dst


if __name__ == "__main__":
    ary = list(range(1, 1_000_000))
    import datetime
    #
    if True:
        print(f"test, chunk, beg")
        t1 = datetime.datetime.now()
        for i in range(1, 1000):
            chunk_data = chunk(ary, i, is_iter=False)
            del chunk_data
        t2 = datetime.datetime.now()
        dd = (t2 - t1)
        print(f"test, chunk, end, {dd}")
    if True:
        print(f"test, list_chunk, beg")
        t1 = datetime.datetime.now()
        for i in range(1, 1000):
            chunk_data = list_chunk(ary, i)
            del chunk_data
        t2 = datetime.datetime.now()
        dd = (t2 - t1)
        print(f"test, list_chunk, end, {dd}")
    #
    print("list_chunk[v], chunk[x],")
