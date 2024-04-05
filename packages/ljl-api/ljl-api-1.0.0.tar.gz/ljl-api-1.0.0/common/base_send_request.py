# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: base_send_request.py
@date: 2022/08/28 16:42
"""
import json

import allure
from pip._vendor import requests

from common.base_request import BaseRequest
from common.base_response import BaseResponse
from common.keys_driver import KeysDriver
from tools.utils import json_to_dict


class BaseSendRequest():
    base_request = None
    base_response = None
    def __init__(self,base_request):
        self.base_request = base_request
    def send_request(self):
        r = requests.request(
            method=self.base_request.method,
            url=self.base_request.url,
            json=self.base_request.json,
            data=self.base_request.data,
            headers=self.base_request.headers,
            files=self.base_request.files,
            params=self.base_request.params
        )
        self.base_response = BaseResponse(r)

class SendRequest(BaseSendRequest):
    local_vars = {}  # 相当于jmeter的变量池，存放代码中，通过关键字获取到的数据
    def __init__(self,case_dict):
        """
        用例数据组成的字典
        """
        # 获取前置操作数据
        self.pre_processers = case_dict["pre_processers"]
        # 获取请求相关信息
        base_request = BaseRequest()
        request_dict = {}
        request_dict["method"] =  case_dict["method"]
        request_dict["app"] =  case_dict["app"]
        request_dict["url"] =  case_dict["url"]
        request_dict["headers"] =  case_dict["headers"]
        request_dict["params"] =  case_dict["params"]
        request_dict["data"] =  case_dict["data"]
        request_dict["json"] =  case_dict["json"]
        request_dict["files"] =  case_dict["files"]
        self.request_dict = request_dict
        super().__init__(base_request)
        # 获取后置操作
        self.post_processers = case_dict["post_processers"]
        # 获取断言
        self.assert_data = case_dict["assert"]
        # 获取allure报告数据
        # d = {}
        # d["feature"] = case_dict["feature"]
        # d["story"] = case_dict["story"]
        # self.allure_data = d
        allure_list = ["feature","story"]
        self.allure_data = {k:case_dict[k] for k in case_dict if k in allure_list }

    def send_request(self):
        '''
        发送请求
        :return:
        '''
        # 添加allure报告信息
        print(self.allure_data)
        for k in self.allure_data:
            getattr(allure.dynamic,k)(self.allure_data[k])
        # 第一步、前置动作（关键字）
        KeysDriver(self,self.pre_processers)
        # 第二步、请求发送
        # 关键字替换
        self.request_dict = json_to_dict(KeysDriver(self,json.dumps(self.request_dict,ensure_ascii=False)).value)
        # 初始化base_request
        self.base_request.url= (self.request_dict["app"],self.request_dict.pop("url")) # 先把url赋值给base__request对象
        for k,v in self.request_dict.items():
            setattr(self.base_request,k,v)
        # 关键字替换完成之后，把请求发送出去
        super().send_request()
        # 第三步、后置动作（关键字）
        KeysDriver(self,self.post_processers)
        # 第四步、断言（关键字）
        KeysDriver(self,self.assert_data)
