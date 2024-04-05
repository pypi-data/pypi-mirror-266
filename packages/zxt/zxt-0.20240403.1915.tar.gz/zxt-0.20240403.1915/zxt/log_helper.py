# !/usr/bin/env python3
# coding=utf8
"""
omit
"""


import datetime
import logging
import os
import pathlib


class LogHelper(object):
    """
    我需要在一个系统里面打日志, 我不知道这个系统有没有用 logging,
    哪里用了 logging, 怎么初始化的 logging, 怎么使用的 logging,
    反正我准备用 logging 打日志, 所以我的操作不能影响系统里原有的 logging,
    于是有了这个类, 参考自: vnpy/vnpy/trader/engine.py 里的 LogEngine,
    """

    CRITICAL: int = logging.CRITICAL  # 同 FATAL
    FATAL: int = logging.FATAL  # 同 CRITICAL
    ERROR: int = logging.ERROR
    WARNING: int = logging.WARNING
    INFO: int = logging.INFO
    DEBUG: int = logging.DEBUG
    NOTSET: int = logging.NOTSET

    def __init__(self, name: str, level: int = logging.INFO) -> None:
        """
        name 是 None/"root" 时, 会得到 logging.RootLogger
        """
        self.name: str = name
        self.level: int = level

        self.is_first: bool = not self.exist(name=self.name)  # 若尚不存在, 则本次必定是首次初始化,

        self.logger: logging.Logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)

        self.formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s  %(levelname)s: %(message)s"
        )

        self.add_null_handler()

    def add_null_handler(self) -> None:
        """"""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.NullHandler):
                return

        null_handler: logging.NullHandler = logging.NullHandler()
        self.logger.addHandler(null_handler)

    def add_console_handler(self) -> None:
        """"""
        console_handler: logging.StreamHandler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def add_file_handler(self, path=None, dir=None, file=None) -> None:
        """"""
        if path is None:
            if dir is None:
                dir: str = pathlib.Path(__file__).parent.as_posix()

            if file is None:
                dttm: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file: str = f"{dttm}_{self.name}.log"

            path: str = pathlib.Path(dir).joinpath(file).as_posix()
        else:
            assert dir is None and file is None

        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)

        file_handler: logging.FileHandler = logging.FileHandler(
            filename=path, mode="a", encoding="utf8",
        )
        file_handler.setLevel(self.level)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    @classmethod
    def exist(cls, name: str) -> bool:
        """
        logging 里面是否有名为 name 的 Logger,
        参考了 logging.getLogger 函数,
        """
        if not name or isinstance(name, str) and name == logging.Logger.root.name:
            return True

        obj = logging.Logger.manager.loggerDict.get(name, None)
        is_exist: bool = isinstance(obj, logging.Logger)
        return is_exist

    def debug(self, msg, *args, **kwargs):
        """"""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """"""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """"""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """"""
        self.logger.error(msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        """同 critical 函数"""
        self.logger.fatal(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """同 fatal 函数"""
        self.logger.critical(msg, *args, **kwargs)


if __name__ == "__main__":
    logh = LogHelper(name="test", level=logging.INFO)
    logh.add_console_handler()
    logh.add_file_handler()

    pai: float = 3.14
    num: int = 7

    logh.info("pai=%s, num=%s,", pai, num)  # 使用 logger 的格式化
    logh.info("pai={}, num={},".format(pai, num))  # 使用 format 函数
