# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: post_process_methods.py
@date: 2022/09/18 11:01
"""
# 后置关键字
import random

import jsonpath

from common.custom_exception import KeysExcutorFailed
from tools.log import Logger


def post_process(func):
    def __warp(send_request,*args,**kwargs):
        # 如果base_response属性中的值位None，说明该请求还未发出去或者是发送失败了。后置动作关键字，不可以被运行
        if send_request.base_response is None:
            Logger().error(f"该关键字，必须使用在后置动作中")
            raise KeysExcutorFailed
        res = func(send_request,*args,**kwargs)
        return res
    return __warp

# 令牌,$.data.list[9,2],1
# ("令牌","$.data.list[9","2]","1")
# *("令牌","$.data.list[9","2]","1")
# var_name = "令牌"   json_path = ("$.data.list[9","2]","1")
@post_process
def json_excutor(send_request,var_name,*json_path):
    # 获取接口响应数据
    response = send_request.base_response.response_body_dict
    # json_path（元组）:   json_path 索引号     索引号一定是一个数字，jsonpath，不可能是以数字结尾
    index = 0
    if json_path[-1].strip().isdigit(): # 如果元组中，最后一个元素，是一个数字。说明入参中，包含索引号
        index = int(json_path[-1].strip())
        json_path = json_path[:-1]
    json_path = ','.join(json_path) # 把元组，拼接成字符串
    res = jsonpath.jsonpath(response,json_path) # 根据jsonpath字符串，从字典中，提取到指定数据，存入列表中。res
    if index == 0: # 如果索引为0，则从jsonpath提取结果列表中，随机获取一个数据，存入变量
        s = random.choice(res)
        Logger().debug(f"json提取器从响应中提取到了提取到数据: {s}，存入变量：{var_name}")
        send_request.local_vars[var_name] = s
    elif len(res) >= index:
        Logger().debug(f"从响应中提取到了提取到数据:{res[index-1]}，存入变量：{var_name}")
        send_request.local_vars[var_name] = res[index-1]
    else:
        Logger().error(f"json提取器中，索引长度不能超过结果最大值。索引：{index}")
        raise KeysExcutorFailed

