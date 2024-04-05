# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: log.py
@date: 2022/08/28 10:53
"""
import logging
import os
import time


def single_instance(func):
    d = {}
    def __wap(name="app"):
        if name in d:
            return d[name]
        else:
            d[name] = func(name)
        return d[name]
    return __wap


@single_instance
class Logger():
    __file_name = None

    def __init__(self,name="app"):
        self.get_logger(name)
        self.get_haddler()
    @property
    def __log_file(self):
        if self.__file_name is None:
            # 把时间戳转换成时间元组
            time_tuple = time.localtime(time.time())
            # 把是时间元组，转换成时间字符串
            time_str = time.strftime("%Y%m%d",time_tuple)
            __class__.__file_name = os.path.join(os.getcwd(),"logs",f"{time_str}-")
        return self.__file_name

    def get_logger(self,name):
        # 创建日志记录器
        self.logger = logging.getLogger(name)
        # 设置日志记录器的级别
        self.logger.setLevel(level=logging.DEBUG)  # 设置日志收集的最低级别

    def get_haddler(self):
        '''
        创建日志收集器
        :return:
        '''
        # 创建formatter
        formater = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(lineno)d : %(message)s")
        # 创建一个debug级别的日志处理器
        handler_debug = logging.FileHandler(f"{self.__log_file}debug.log") # os.getcwd() 获取项目运行时路径
        handler_debug.setLevel(level=logging.DEBUG) # 设置日志处理的级别
        handler_debug.setFormatter(formater) # 绑定日志格式化器
        # 创建一个error级别的日志处理器
        handler_error = logging.FileHandler(f"{self.__log_file}error.log")
        handler_error.setLevel(level=logging.ERROR)
        handler_error.setFormatter(formater)
        # 和日志收集器绑定
        self.logger.addHandler(handler_debug)
        self.logger.addHandler(handler_error)

    def debug(self,msg):
        self.logger.debug(msg)

    def info(self,msg):
        self.logger.info(msg)

    def warning(self,msg):
        self.logger.warning(msg)

    def error(self,msg):
        self.logger.error(msg)

    def critical(self,msg):
        self.logger.critical(msg)

if __name__ == '__main__':
    Logger("aaa").info("aaaa")
    Logger("bbb").error("error")
    Logger().debug("debug")
    Logger().warning("warning")
