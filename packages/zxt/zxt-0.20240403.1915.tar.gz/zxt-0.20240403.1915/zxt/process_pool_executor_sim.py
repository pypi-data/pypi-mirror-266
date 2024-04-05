# !/usr/bin/env python3
# coding=utf8
"""
如果子进程被kill了该怎么办?
"""
import concurrent.futures
import itertools
import logging
import multiprocessing
import multiprocessing.pool
import os
import queue
import threading
import time
import types
from concurrent.futures.process import _CallItem, _ResultItem
from typing import Any, Dict, List, Set, Tuple, Type, Optional, Union, Callable


class ProcessPoolExecutorSim(object):
    """"""

    class _Task(object):
        """"""

        def __init__(self, work_id: int, result_item: _ResultItem) -> None:
            """"""
            self._work_id: int = work_id
            self._result_item: _ResultItem = result_item

        def result(self):
            """"""
            return self.__get_result()

        def __get_result(self):
            """"""
            if self._result_item.exception:
                try:
                    raise self._result_item.exception
                finally:
                    pass
            else:
                return self._result_item.result

    @classmethod
    def _process_worker(cls, call_queue: multiprocessing.Queue, rslt_queue: multiprocessing.Queue) -> None:
        """往 call_queue 传入 None 可以结束循环"""
        # 在 Python310/Lib/concurrent/futures/process.py 搜索
        # 『if isinstance(result_item, int):』可以知道传入None得到int后的处理逻辑
        concurrent.futures.process._process_worker(
            call_queue=call_queue,
            result_queue=rslt_queue,
            initializer=None,
            initargs=None,
        )
        return

    def __enter__(self):
        """"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """"""
        self.shutdown()

        is_ok: bool = False
        with self._debug_lock:
            is_ok: bool = (self._debug_call_num == self._debug_rslt_num)
        if not is_ok:
            raise RuntimeError(f"call_num={self._debug_call_num}, rslt_num={self._debug_rslt_num},")

        return False

    def __init__(self, max_workers=None, *args, **kwargs):
        """"""
        self._debug_lock = threading.Lock()
        self._debug_call_num: int = 0
        self._debug_rslt_num: int = 0
        self._max_workers = self.fix_max_workers(max_workers=max_workers)
        self._job_counter = itertools.count()
        self.call_queue: multiprocessing.Queue = multiprocessing.Queue(maxsize=0)
        self.rslt_queue: multiprocessing.Queue = multiprocessing.Queue(maxsize=0)
        self.task_items: Dict[int, ProcessPoolExecutorSim._Task] = {}
        self.processes: Dict[int, multiprocessing.Process] = {}
        self.initialize()

    def initialize(self):
        """"""
        for _ in range(self._max_workers):
            process = multiprocessing.Process(target=self._process_worker, args=(self.call_queue, self.rslt_queue))
            process.start()  # start()之后pid才有值,
            self.processes[process.pid] = process

    def terminate(self) -> None:
        """"""
        self.join_executor_internals()

    def shutdown(self) -> None:
        """"""
        self.join_executor_internals()

    def as_completed(self, fs, timeout=None):
        """"""
        fs = set(fs)

        while fs:
            self._process_result()

            lines: list = []

            for task in fs:
                task: ProcessPoolExecutorSim._Task = task
                if task._result_item is not None:
                    lines.append(task)

            for task in lines:
                yield task
                fs.discard(task)

            if not lines:
                time.sleep(0.001)

    def submit(self, fn, /, *args, **kwargs) -> _Task:
        """"""
        work_id: int = next(self._job_counter)

        task = self._Task(work_id=work_id, result_item=None)
        self.task_items[task._work_id] = task

        call_item = _CallItem(work_id, fn, args, kwargs)
        self.call_queue.put(call_item, block=True)

        with self._debug_lock:
            self._debug_call_num += 1

        return task

    def _process_result(self):
        """"""
        while True:
            try:
                result_item = self.rslt_queue.get_nowait()
                if isinstance(result_item, _ResultItem):
                    with self._debug_lock:
                        self._debug_rslt_num += 1
                self.process_result_item(result_item=result_item)
            except queue.Empty as ex:
                break

    @classmethod
    def fix_max_workers(cls, max_workers: Optional[int] = None) -> int:
        """"""
        # 部分代码参考自 Python310/Lib/concurrent/futures/process.py
        assert isinstance(max_workers, (types.NoneType, int))

        if max_workers is None:
            max_workers = os.cpu_count() or 1

        if max_workers <= 0:
            raise ValueError("max_workers must be greater than 0")

        return max_workers

    def process_result_item(self, result_item: Union[int, _ResultItem]):
        # Process the received a result_item. This can be either the PID of a
        # worker that exited gracefully or a _ResultItem

        if isinstance(result_item, int):
            # Clean shutdown of a worker using its PID
            # (avoids marking the executor broken)
            p = self.processes.pop(result_item)
            p.join()
            if not self.processes:
                self.join_executor_internals()
                return
        else:
            # Received a _ResultItem so mark the future as completed.
            work_item = self.task_items.pop(result_item.work_id, None)
            # work_item can be None if another process terminated (see above)
            if work_item is not None:
                work_item._result_item = result_item

    def shutdown_workers(self):
        n_children_to_stop = self.get_n_children_alive()
        n_sentinels_sent = 0
        # Send the right number of sentinels, to make sure all children are
        # properly terminated.
        while (n_sentinels_sent < n_children_to_stop
                and self.get_n_children_alive() > 0):
            for i in range(n_children_to_stop - n_sentinels_sent):
                try:
                    self.call_queue.put_nowait(None)
                    n_sentinels_sent += 1
                except queue.Full:
                    break

    def join_executor_internals(self):
        self.shutdown_workers()
        # Release the queue's resources as soon as possible.
        self.call_queue.close()
        self.call_queue.join_thread()
        # If .join() is not called on the created processes then
        # some ctx.Queue methods may deadlock on Mac OS X.
        for p in self.processes.values():
            p.join()

    def get_n_children_alive(self):
        # This is an upper bound on the number of children alive.
        return sum(p.is_alive() for p in self.processes.values())


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

    with ProcessPoolExecutorSim(
        max_workers=None,
        mp_context=multiprocessing.get_context("spawn")
    ) as executor:

        future_pending: List[ProcessPoolExecutorSim._Task] = [
            executor.submit(__cstdlib_div, task[0], task[1]) for task in task_list
        ]

        future_finished: List[ProcessPoolExecutorSim._Task] = []

        for future in executor.as_completed(future_pending):
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
