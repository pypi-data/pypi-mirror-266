# !/usr/bin/env python3
# coding=utf8
""""""
import concurrent.futures
import logging
import multiprocessing
from typing import Any, Dict, List, Set, Tuple, Type, Optional, Union, Callable


def __cstdlib_div(numer: int, denom: str) -> dict:
    """C库函数, div(27, 4): 分子numer=27, 分母denom=4, 商quot=6, 余数rem=3"""
    quot: int = numer // denom
    rem: int = numer % denom
    mapping: dict = {
        "numer": numer,
        "denom": denom,
        "quot": quot,
        "rem": rem,
    }
    return mapping


def __main_function():
    """
    https://www.dongwm.com/post/use-concurrent-futures/
    """
    task_list = [
        (27, 4),
        (27, 3),
        (27, 0),
    ]
    task_list = task_list[:]

    with concurrent.futures.ProcessPoolExecutor(
        max_workers=None,
        mp_context=multiprocessing.get_context("spawn")
    ) as executor:

        future_pending: List[concurrent.futures.Future] = [
            executor.submit(__cstdlib_div, task[0], task[1]) for task in task_list
        ]

        future_finished: List[concurrent.futures.Future] = []

        for future in concurrent.futures.as_completed(future_pending):
            future_finished.append(future)

        print("-" * 80 + ", tag_1")

        results: list = []

        for future in future_finished:
            results.append(future.result())

        print("-" * 80 + ", tag_2")

        for result in results:
            print(result)

        print("-" * 80 + ", tag_3")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(message)s")
    __main_function()
