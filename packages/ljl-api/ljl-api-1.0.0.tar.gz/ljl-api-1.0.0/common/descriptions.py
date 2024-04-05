# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: descriptions.py
@date: 2022/08/28 15:35
"""
import json
import os

from tools.config import Config
from tools.log import Logger
from tools.utils import headers_to_dict, params_to_dict, str_to_dict, json_to_dict


class BaseDesc():
    __config = None
    @property
    def config(self):
        if self.__config is None:
            __class__.__config = Config()
        return self.__config

class ConfigDesc(BaseDesc):
    def __set__(self, instance, value):
        pass
    def __get__(self, instance, owner):
        return self.config


class MethodDesc():
    __value = None
    def __get__(self, instance, owner):
        return self.__value

    def __set__(self, instance, value):
        self.__value = value.strip()

class UrlDesc(BaseDesc):
    __value = None
    __app = None
    def __get__(self, instance, owner):
        base_url = self.config.get_url(self.__app)
        return f"{base_url.rstrip('/')}/{self.__value.lstrip('/')}"

    def __set__(self, instance, value):
        '''
        value 必须是一个元组 (应用名,接口地址)
        :param instance:
        :param value:
        :return:
        '''
        self.__app = value[0]
        self.__value = value[1]


class HeadersDesc():
    __value = None
    def __set__(self, instance, value):
        value = str_to_dict(value) # 尝试把一个字典类型的字符串，转成一个字典
        if isinstance(value,str):
            self.__value = headers_to_dict(value)
        else:
            self.__value = value

    def __get__(self, instance, owner):
        return self.__value


class ParamsDesc():
    __value = None
    def __set__(self, instance, value):
        value = str_to_dict(value)  # 尝试把一个字典类型的字符串，转成一个字典
        if isinstance(value, str):
            self.__value = params_to_dict(value)
        else:
            self.__value = value


    def __get__(self, instance, owner):
        return self.__value

class JsonDesc():
    __value = None
    def __set__(self, instance, value):
        if isinstance(value,str):
            self.__value = json_to_dict(value)
        else:
            self.__value = value

    def __get__(self, instance, owner):
        return self.__value


class DataDesc():
    __value = None
    def __set__(self, instance, value):
        value = str_to_dict(value)  # 尝试把一个字典类型的字符串，转成一个字典
        if isinstance(value,str) and "=" in value:
            self.__value = params_to_dict(value)
        else:
            self.__value = value

    def __get__(self, instance, owner):
        return self.__value

class FilesDesc(BaseDesc):
    __value = None
    def __get__(self, instance, owner):
        if isinstance(self.__value,list) or  isinstance(self.__value,tuple):
            res = []
            for l in self.__value:
                file_path = os.path.join(self.config.get_root_path(),l[1])
                try:
                    res.append((l[0],open(file_path,'rb')))
                except:
                    Logger().error(f"待上传文件路径不存在：{file_path}")
                    raise
            return res
        else:
            return self.__value

    def __set__(self, instance, value):
        '''
    [("关键字":"文件路径")]
    '''
        self.__value = str_to_dict(value)  # 尝试把一个字典类型的字符串，转成一个字典
