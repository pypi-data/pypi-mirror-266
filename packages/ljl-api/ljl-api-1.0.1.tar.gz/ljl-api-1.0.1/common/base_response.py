# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: base_response.py
@date: 2022/08/28 16:55
"""
import os

from common.descriptions import ConfigDesc
from tools.log import Logger
from tools.utils import dict_to_headers


class BaseResponse():
    config = ConfigDesc()

    def __init__(self,response):
        self.response = response
        self.__print_log()

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def response_body_text(self):
        return self.response.text

    @property
    def response_body_dict(self):
        return self.response.json()
    @property
    def response_body_content(self):
        return self.response.content

    def save_to_file(self,file_path):
        file_path = os.path.join(self.config.get_root_path(),file_path)
        with open(file_path,"wb") as f:
            f.write(self.response_body_content)
    @property
    def response_headers(self):
        return dict_to_headers(self.response.headers)

    @property
    def request_url(self):
        return self.response.request.url

    @property
    def request_method(self):
        return self.response.request.method

    @property
    def request_headers(self):
        return dict_to_headers(self.response.request.headers)

    @property
    def request_body(self):
        return self.response.request.body or ""

    def __print_log(self):
        # 打印请求和响应报文至日志
        Logger().debug(f"""
--------------------------请求报文-----------------------------
{self.request_method} {self.request_url}
{self.request_headers}

{self.request_body}""")

        Logger().debug(f"""
--------------------------响应报文-----------------------------
{self.status_code}
{self.response_headers}

{self.response_body_text}""")