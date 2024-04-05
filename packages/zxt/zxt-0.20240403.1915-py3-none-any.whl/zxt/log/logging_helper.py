# !/usr/bin/env python3
# coding=utf8
"""
omit
"""


def logging_basicConfig():
    """"""
    import logging
    logging.basicConfig(
        format="%(asctime)s (%(process)5d, %(thread)d) %(name)s %(levelname)s - %(message)s",
        level=logging.DEBUG
    )


def logging_config_dictConfig(logging_filename: str = None):
    """
    Parameters:
        logging_filename: 日志文件名;
    Returns:
        None

    日志初始化函数,
    日志无脑写文件,
    如果日志等级较低, 使用 cout 才能输出到屏幕, 如果日志等级较高, 无脑输出到屏幕,
    书写 logging.getLogger('cout').debug('特定的日志') 即可
    参考自: https://www.cnblogs.com/shouke/p/14256086.html
    参考自: https://www.pynote.net/archives/2006
    """
    import datetime
    import logging
    import logging.config
    import os

    logging_filename = logging_filename if logging_filename else 'log_%Y%m%d_%H%M%S_%f.log'
    logging_filename = datetime.datetime.now().strftime(logging_filename)  # 替换类似 %Y%m%d_%H%M%S_%f 形式的字符串;

    if os.path.dirname(logging_filename):
        os.makedirs(os.path.dirname(logging_filename), exist_ok=True)

    config = {
        "version": 1,
        "formatters": {
            "formatter_1": {
                "format": "%(asctime)s (%(process)5d, %(thread)d) %(name)s "
                "%(filename)s(%(funcName)s[line:%(lineno)d]) "
                "%(levelname)s - %(message)s"
            },
            "formatter_2": {
                "format": "%(asctime)s (%(process)5d, %(thread)d) %(name)s %(levelname)s - %(message)s"
            }
        },
        "filters": {
            "filter_cout": {
                "class": "logging.Filter",
                "name": "cout",
                "note": "如果只想输出特定的日志到控制台, 书写 logging.getLogger('cout').debug('特定的日志') 即可",
                "memo": "想和 root 等长, 要有输出到屏幕的意思, 然后选择了 C++ 的 std::cout 的拼写"
            }
        },
        "handlers": {
            "handler_file": {
                "filename": "log.log" if logging_filename is None else logging_filename,
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "formatter_1"
            },
            "handler_console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "formatter_2"
            },
            "handler_console_cout": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "formatter_2",
                "filters": ["filter_cout"]
            }
        },
        "root": {
            "handlers": ["handler_file", "handler_console"],
            "level": "DEBUG"
        },
        "incremental": False
    }

    logging.config.dictConfig(config)

    class coutFilter(logging.Filter):
        def filter(self, record: logging.LogRecord):
            if logging.WARNING <= record.levelno:
                return True
            if record.name == "cout":
                return True
            return False

    # 用代码设置 Filter
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):
            continue
        assert isinstance(handler, logging.StreamHandler)
        assert handler.name == "handler_console"
        assert len(handler.filters) == 0
        handler.addFilter(coutFilter())

    # 如果在调用此函数之前, 曾经执行过类似 logging.getLogger('cout').debug('特定的日志') 的语句,
    # 需要执行下面的逻辑, 程序的行为才符合预期,
    try:
        logging._acquireLock()
        #
        manager: logging.Manager = logging.Logger.manager
        if 'cout' in manager.loggerDict:
            del manager.loggerDict['cout']
    finally:
        logging._releaseLock()

    return


if __name__ == '__main__':
    import logging
    import os

    logging_basicConfig()

    print('section_1')
    logging.debug('msg_debug')
    logging.info('msg_info')
    logging.warning('msg_warning')
    logging.error('msg_error')

    print('section_2')
    logging.getLogger('cout').debug('msg_debug')
    logging.getLogger('cout').info('msg_info')
    logging.getLogger('cout').warning('msg_warning')
    logging.getLogger('cout').error('msg_error')

    fname = os.path.join(os.path.dirname(__file__), 'log_folder', os.path.basename(__file__) + '.%Y%m%d_%H%M%S.log')
    logging_config_dictConfig(logging_filename=fname)

    print('section_3')
    logging.debug('msg_debug')
    logging.info('msg_info')
    logging.warning('msg_warning')
    logging.error('msg_error')

    print('section_4')
    logging.getLogger('cout').debug('msg_debug')
    logging.getLogger('cout').info('msg_info')
    logging.getLogger('cout').warning('msg_warning')
    logging.getLogger('cout').error('msg_error')

    print('section_5')
    logging.debug('msg_debug')
    logging.info('msg_info')
    logging.warning('msg_warning')
    logging.error('msg_error')

    print('section_6')
    logging.getLogger('cout').debug('msg_debug')
    logging.getLogger('cout').info('msg_info')
    logging.getLogger('cout').warning('msg_warning')
    logging.getLogger('cout').error('msg_error')

    print('DONE!')
