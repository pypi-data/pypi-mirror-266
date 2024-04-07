# -*- coding: utf-8 -*-
"""
# @项目名称 :pytorch
# @文件名称 :new_log.py
# @作者名称 :sxzhang1
# @日期时间 :2024/2/29 13:25
# @文件介绍 :
"""
import inspect
import os
import re
import time
from datetime import datetime
from typing import Union

from colorama import Fore, init


class LogLevel:
    """
    日志登记
    """

    def __init__(self):
        ...

    @property
    def exception(self):
        return 60

    @property
    def critical(self):
        return 50

    @property
    def fatal(self):
        return 55

    @property
    def error(self):
        return 40

    @property
    def warning(self):
        return 30

    @property
    def warn(self):
        return 25

    @property
    def notice(self):
        return 20

    @property
    def info(self):
        return 15

    @property
    def debug(self):
        return 10

    @property
    def notset(self):
        return 0

    def get_label_of_level(self, level: int):
        """
        获取此数值所对应的日志登记
        :param level: 日志数值
        :return:
        """
        __levelToName = {
            self.exception: 'exception',
            self.critical: 'critical',
            self.fatal: 'fatal',
            self.error: 'error',
            self.notice: 'notice',
            self.warning: 'warning',
            self.warn: 'warn',
            self.info: 'info',
            self.debug: 'debug',
            self.notset: 'notset',
        }
        if level in __levelToName.keys():
            return __levelToName[level].upper()
        else:
            raise KeyError("不包含此键值：{0}".format(level))

    def get_level_by_label(self, level_label: str):
        """
        获取次日志所对应的数值
        :param level_label:日志登记
        :return:
        """
        __nameToLevel = {
            'exception': self.exception,
            'critical': self.critical,
            'fatal': self.fatal,
            'error': self.error,
            'notice': self.notice,
            'warn': self.warn,
            'warning': self.warning,
            'info': self.info,
            'debug': self.debug,
            'notset': self.notset,
        }
        if level_label in __nameToLevel.keys():
            return __nameToLevel[level_label.lower()]
        else:
            raise KeyError("不包含此键值：{0}".format(level_label))


class Logger(object):
    def __init__(self, **kwargs):
        """
        日志
        :param title:日志名称
        :param log_dir: 日志路径，
        :param file_level: 日志等级
        :param categorize:路径是否包含title
        :param date_rotate:是否添加日期路径
        :param datetime_format:日期格式
        :param print_level:控制台打印的最低等级
        :param record_millisecond:日志时间是否包含毫秒
        :param file_encoding:日志编码，默认为
        :param is_color:控制台输出是否彩色输出
        :param format:打印输出格式,目前只包含[datetime]、[func_name]、[log_level]、[lineno]、[message]
        """
        self.__log_level = LogLevel()
        self.params = dict()
        self.params.update(kwargs)
        self.__init_params()
        self.__filter__ = dict()

    def __dt(self):
        """
        获取当前日期
        :return:
        """
        return datetime.now().strftime(self.params["datetime_format"])

    def __init_params(self):
        """
        初始化日志参数
        :return:
        """
        self.params["title"] = self.params.get("title", self.__class_name())
        self.params["date_rotate"] = self.params.get("date_rotate", False)
        self.params["log_dir"] = self.params.get("log_dir")
        self.params["print_level"] = self.params.get("print_level", self.__log_level.notset)
        self.params["file_level"] = self.params.get("file_level", self.__log_level.notset)
        self.params["is_color"] = self.params.get("is_color", False)
        self.params["file_encoding"] = self.params.get("file_encoding", "utf-8")
        self.params["datetime_format"] = self.params.get("datetime_format", "%Y-%m-%d %H:%M:%S")
        self.params["format"] = self.params.get("format", "[datetime] [[class_name]-[func_name]]|"
                                                          "<[log_level]>|([lineno]):[message|extra]")
        self.__params_dict = {
            "[datetime]": self.__dt(),
            "[class_name]": self.__class_name(),
            "[lineno]": self.__line_no(),
            "[log_level]": "",
            "[message|extra]": "[message|extra]",
        }
        init()

    @property
    def __filter(self):
        """
        过滤日志操作
        :return:
        """
        flag = True
        for value in self.__filter__:
            term_bool = "[{0}]".format(value.get("term")) in self.__params_dict.keys()
            cond_bool = value.get("cond") in ["in", "on", ">", "<", "<>", "><", "<=", ">=", "=", "l", "r"]
            if term_bool and cond_bool:
                if self.__filter_content(value):
                    flag = False
                    break
                else:
                    continue
            else:
                raise ValueError("请添加正确的筛选条件：（in、on、>、<、<>、><、=、<=、>=、l、r）")
        return flag

    def __filter_content(self, value):
        """
        条件进行判断
        :param value:
        :return:
        """
        term = "[{0}]".format(value.get("term", ""))
        val = value.get("value", "")
        term_value = self.__params_dict.get(term)
        if value.get("cond") == "in":
            value_type = isinstance(val, str)
            message = isinstance(term_value, (str, list))
            if all([value_type, message, val in term_value]):
                return True
        elif value.get("cond") == "on":
            value_type = isinstance(val, (str, list))
            message = isinstance(term_value, type(val))
            if all([value_type, message, term_value in val]):
                return True
        elif value.get("cond") == ">":
            value_type = isinstance(val, (int, str))
            message = isinstance(term_value, type(val))
            if all([value_type, message, val > term_value]):
                return True
        elif value.get("cond") == "<":
            value_type = isinstance(val, (int, str))
            message = isinstance(term_value, type(val))
            if all([value_type, message, val < term_value]):
                return True
        elif value.get("cond") == "<>":
            value_type = type(val) is list and len(val) == 2
            message = isinstance(term_value, (str, int))
            if all([value_type, message, val[0] < term_value < val[1]]):
                return True
        elif value.get("cond") == "><":
            value_type = type(val) is list and len(val) == 2
            message = isinstance(term_value, (str, int))
            if all([value_type, message, any([val[0] > term_value, term_value > val[1]])]):
                return True
        elif value.get("cond") == "=":
            value_type = type(val) in [int, str]
            message = isinstance(term_value, val)
            if all([value_type, message, val == term_value]):
                return True
        elif value.get("cond") == "<=":
            value_type = type(val) in [int, str]
            message = isinstance(term_value, val)
            if all([value_type, message, val <= term_value]):
                return True
        elif value.get("cond") == ">=":
            value_type = type(val) in [int, str]
            message = isinstance(term_value, val)
            if all([value_type and message and val >= term_value]):
                return True
        elif value.get("cond") == "l":
            value_type = isinstance(val, str)
            message = isinstance(term_value, str)
            if all([value_type, message, term_value.startswith(val)]):
                return True
        elif value.get("cond") == "r":
            value_type = isinstance(val, str)
            message = isinstance(term_value, str)
            if all([value_type, message, term_value.endswith(val)]):
                return True
        else:
            raise ValueError("请添加正确的筛选条件：（in、on、>、<、<>、><、>=、<=、=、l、r）")
        return False

    @property
    def filter(self):
        return self.__filter__

    @filter.setter
    def filter(self, content: Union[list, str, dict]):
        """
        设置过滤条件
        :param content:示例{'term':'message','value':'错误','cond':'in'}
        cond包含：in、on、>、<、<>、=、l、r
        :return:
        """
        if type(content) is list:
            self.__filter__ = content
        elif type(content) is str:
            self.__filter__ = [{'term': "message", 'value': content, "cond": "in"}]
        elif type(content) is dict:
            self.__filter__ = [content]
        else:
            raise "筛选条件错误：{'term':'message','value':'错误','cond':'in'}"

    def __file_handler(self, log_level="debug"):
        """
        获取文件句柄
        :return:
        """
        if self.params.get("log_dir"):
            today = ""
            if self.params.get("date_rotate"):
                localtime = time.localtime()
                today = os.path.join(str(localtime.tm_year), str(localtime.tm_mon), str(localtime.tm_mday))
            filepath = os.path.join(self.params.get("log_dir"), today)
            os.makedirs(filepath, exist_ok=True)
            filepath = os.path.join(filepath, "{0}.{1}".format(self.params.get("title"), log_level.lower()))
            file = open(filepath, 'a', encoding=self.params.get("file_encoding"))
            return file
        else:
            return None

    @staticmethod
    def __thread():
        """
        获取线程信息
        :return:
        """
        ...

    @staticmethod
    def __process():
        """
        获取进程信息
        :return:
        """
        ...

    def __class_name(self):
        """
        获取调用类名
        :return:
        """
        caller_locals = inspect.currentframe().f_back.f_back.f_back.f_locals
        caller_class_name = caller_locals.get('self', self).__class__.__name__
        return caller_class_name

    @staticmethod
    def __func_name():
        """
        获取调用函数名
        :return:
        """
        caller_func_name = inspect.currentframe().f_back.f_back.f_back.f_back.f_code.co_name
        return caller_func_name

    @staticmethod
    def __line_no():
        """
        获取行号信息
        :return:
        """
        frame = inspect.currentframe().f_back.f_back
        return "{0:0>5d}".format(frame.f_lineno)

    @property
    def print_level(self):
        return self.params.get("print_level")

    @print_level.setter
    def print_level(self, print_level):
        self.params["print_level"] = print_level

    @property
    def datetime_format(self):
        return self.params.get("datetime_format")

    @datetime_format.setter
    def datetime_format(self, datetime_format):
        self.params["datetime_format"] = datetime_format

    @property
    def log_level(self):
        return self.params.get("log_level")

    @log_level.setter
    def log_level(self, log_level):
        self.params["log_level"] = log_level

    @property
    def file_encoding(self):
        return self.params.get("file_encoding")

    @file_encoding.setter
    def file_encoding(self, file_encoding):
        self.params["file_encoding"] = file_encoding

    @property
    def log_dir(self):
        return self.params.get("log_dir")

    @log_dir.setter
    def log_dir(self, log_dir: str):
        self.params["log_dir"] = log_dir

    @property
    def date_rotate(self):
        return self.params.get("date_rotate")

    @date_rotate.setter
    def date_rotate(self, date_rotate: str):
        self.params["date_rotate"] = date_rotate

    @property
    def is_color(self):
        return self.params.get("is_color")

    @is_color.setter
    def is_color(self, is_color: bool):
        self.params["is_color"] = is_color

    @property
    def title(self):
        return self.params.get("title")

    @title.setter
    def title(self, title: str):
        self.params["title"] = title

    @property
    def format(self):
        return self.params.get("format")

    @format.setter
    def format(self, message_format: str):
        self.params["format"] = message_format

    def __del__(self):
        ...

    def __extend_params(self, log_level, message, extra):
        self.__params_dict["[log_level]"] = "{0:-<8s}".format(self.__log_level.get_label_of_level(log_level))
        self.__params_dict["[func_name]"] = self.__func_name()
        self.__params_dict["[message]"] = message
        self.__params_dict["[extra]"] = extra
        self.__params_dict["[message|extra]"] = "{0}|{1}".format(message, extra) if extra else message
        self.__params_dict["[datetime]"] = self.__dt()

    def __format_message(self, log_level, message, extra, end=os.linesep):
        """
        格式化信息
        :param log_level:
        :param message:
        :param extra:
        :param end:
        :return:
        """
        format_str = self.params.get("format")
        self.__extend_params(log_level, message, extra)
        if self.__filter:
            for fs in re.findall("(\\[[\\w,|]+])", format_str):
                format_str = format_str.replace(fs, str(self.__params_dict.get(fs)))
            if log_level >= self.params.get("file_level") and self.params.get("log_dir"):
                __open_file = self.__file_handler(self.__log_level.get_label_of_level(log_level))
                __open_file.write(format_str + end)
                __open_file.flush()
                __open_file.close()
            if log_level >= self.params.get("print_level"):
                color_dict = {
                    self.__log_level.exception: Fore.LIGHTRED_EX,
                    self.__log_level.fatal: Fore.LIGHTCYAN_EX,
                    self.__log_level.critical: Fore.CYAN,
                    self.__log_level.error: Fore.RED,
                    self.__log_level.warning: Fore.LIGHTYELLOW_EX,
                    self.__log_level.warn: Fore.YELLOW,
                    self.__log_level.notice: Fore.LIGHTGREEN_EX,
                    self.__log_level.info: Fore.LIGHTWHITE_EX,
                    self.__log_level.debug: Fore.WHITE,
                    self.__log_level.notset: Fore.LIGHTBLACK_EX,
                }
                format_str = color_dict[log_level] + format_str + Fore.RESET if self.is_color else format_str
                print(format_str)
        else:
            pass

    def notset(self, message, extra=None):
        """
        提示日志
        :param message:
        :param extra:
        :return:
        """
        self.__format_message(self.__log_level.notset, message, extra)

    def debug(self, message, extra=None):
        """
        调试日志
        :param message:
        :param extra:
        :return:
        """
        self.__format_message(self.__log_level.debug, message, extra)

    def info(self, message, extra=None):
        """
        日志信息
        :param message:
        :param extra:
        :return:
        """
        self.__format_message(self.__log_level.info, message, extra)

    def notice(self, message, extra=None):
        """
        日志信息
        :param message:
        :param extra:
        :return:
        """
        self.__format_message(self.__log_level.notice, message, extra)

    def warning(self, message, extra=None):
        """
        警告
        :param message:
        :param extra:
        :return:
        """
        self.__format_message(self.__log_level.warning, message, extra)

    def warn(self, message, extra=None):
        """
        警告
        :param message:
        :param extra:
        :return:
        """
        self.__format_message(self.__log_level.warn, message, extra)

    def error(self, message, extra=None):
        """
        错误
        :param message:
        :param extra:
        :return:
        """
        self.__format_message(self.__log_level.error, message, extra)

    def fatal(self, message, extra=None):
        """
        致命的错误
        :param message:
        :param extra:
        :return:
        """
        self.__format_message(self.__log_level.fatal, message, extra)

    def critical(self, message, extra=None):
        """
        严重的错误
        :param message:
        :param extra:
        :return:
        """
        self.__format_message(self.__log_level.critical, message, extra)

    def exception(self, message, extra=None):
        """
        严重的错误
        :param message:
        :param extra:
        :return:
        """
        self.__format_message(self.__log_level.critical, message, extra)
        raise Exception(message)
