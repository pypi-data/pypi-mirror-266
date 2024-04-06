# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: assert_methods.py
@date: 2022/09/18 16:01
"""
import jsonpath

from common.custom_exception import KeysExcutorFailed
from tools.log import Logger
from tools.utils import json_to_dict


def assert_process(func):
    def __warp(send_request,*args,**kwargs):
        # 如果base_response属性中的值位None，说明该请求还未发出去或者是发送失败了。后置动作关键字，不可以被运行
        if send_request.base_response is None:
            Logger().error(f"该关键字，必须使用在断言动作中")
            raise KeysExcutorFailed
        res = func(send_request,*args,**kwargs)
        return res
    return __warp

# json断言
@assert_process
def json_assert(send_request,expect,*json_path):
    json_path = ",".join(json_path)
    # 获取响应数据
    response = send_request.base_response.response_body_dict
    # 使用jsonpath提取对应的数据
    res = jsonpath.jsonpath(response,json_path)# 列表
    actual = res[0]
    try:
        assert expect == actual,f"断言失败，jsonpath对应的数据：{actual} 不等于预期结果: {expect}"
    except:
        Logger().error(f"断言失败，{json_path}对应的数据：{actual} 不等于预期结果: {expect}")
        raise

# 响应断言
@assert_process
def respose_assert(send_request,*expect):
    # 获取响应数据
    response = send_request.base_response.response_body_text
    try:
        assert expect in response,f"断言失败，响应正文中不包含预期结果: {expect}"
    except:
        Logger().error(f"断言失败，响应正文中不包含预期结果: {expect}")
        raise

    pass


# 批量断言
@assert_process
def batch_assert(send_request,*expect):
    '''
    {"message":"SUCESS","resultCode":200}
    :param send_request:
    :param expect:
    :return:
    '''
    expect = ",".join(expect)
    expect = json_to_dict(expect)
    if not isinstance(expect,dict):
        Logger().error(f"批量断言中预期结果只能是json字符串：{expect}")
        assert False,f"批量断言中预期结果只能是json字符串：{expect}"
    response = send_request.base_response.response_body_dict
    compare_dict(response,expect)


def compare_dict(actual,expect):
    if not isinstance(expect,actual):
        Logger().error(f"批量断言中预期结果和响应格式不同")
        assert False, f"批量断言中预期结果只能是json字符串"
    if isinstance(expect,dict):
        for k in expect:
            compare_dict(actual[k], expect[k])
    elif isinstance(expect,list):
        for i in range(len(expect)):
            compare_dict(actual[i], expect[i])
    else:
        try:
            assert actual == expect,f"实际结果：{actual}和预期结果：{expect}不相等"
        except:
            Logger().error(f"实际结果：{actual}和预期结果：{expect}不相等")
            raise


