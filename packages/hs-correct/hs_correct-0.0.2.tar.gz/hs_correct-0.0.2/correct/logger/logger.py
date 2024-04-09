"""
日志工具类封装
"""

import logging
from colorama import Fore, Style


class Logger(object):
    def __init__(self, module_name):
        self.logger = logging.getLogger(name=module_name)
        self.logger.setLevel(logging.INFO)
        # 日志输出格式
        self.formatter = logging.Formatter("[%(asctime)s] [" + module_name + "] [%(levelname)s] %(message)s")

        # 解决被父级调用时输出重复的问题（每次输出会多一份无格式的默认样式日志）
        self.logger.parent = None

    def __console(self, level, message, e):

        # 创建一个StreamHandler,用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)

        if level == "info":
            self.logger.info(Fore.WHITE + str(message) + Style.RESET_ALL)
        elif level == "debug":
            self.logger.debug(Fore.WHITE + str(message) + Style.RESET_ALL)
        elif level == "warning":
            self.logger.warning(Fore.YELLOW + str(message) + Style.RESET_ALL)
        elif level == "error":
            self.logger.error(Fore.RED + str(message) + Style.RESET_ALL)
        elif level == "exception":
            self.logger.exception(e)

        # 避免重复输出
        self.logger.removeHandler(ch)

    def debug(self, message):
        self.__console("debug", message, None)

    def info(self, message):
        self.__console("info", message, None)

    def warning(self, message):
        self.__console("warning", message, None)

    def error(self, message):
        self.__console("error", message, None)

    def exception(self, e):
        self.__console("exception", None, e)
