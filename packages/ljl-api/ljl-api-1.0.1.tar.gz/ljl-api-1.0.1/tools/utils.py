# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: utils.py
@date: 2022/08/28 15:51
"""
import json
# 尝试把一个字符串，转成python字典。字符串仅支持python字典的语法
def str_to_dict(s):
    if s.strip() == "":
        return None
    try:
        return eval(s)
    except:
        return s
# 尝试把json字符串转成python字典，字符串仅支持json的语法
def json_to_dict(s):
    if s.strip() == "":
        return None
    try:
        return json.loads(s)
    except:
        return s

def headers_to_dict(s):
    """
    请求头键值对，转字典格式
    :param s:
    :return:
    """
    d = {}
    lines = s.split("\n")
    for l in lines:
        line = l.split(":",1)
        if len(line) == 2:
            d[line[0]] = line[1].strip()
    return d

def params_to_dict(s):
    '''
    查询参数键值对，转字典格式
    :param s:
    :return:
    '''
    d = {}
    lines = s.split("&")
    for l in lines:
        line = l.split("=",1)
        if len(line) == 2:
            d[line[0]] = line[1].strip()
    return d



#
def dict_to_headers(d):
    return '\n'.join([f"{k}: {v}" for k,v in d.items()])


# if __name__ == '__main__':
#     s = '''Host: api.xuepl.com.cn:28019
# Connection: keep-alive
#
# '''
#     print(headers_to_dict(s))
# if __name__ == '__main__':
#     s = '''{'token':"$__GETVAR(令牌)$"}'''
#     res = str_to_dict(s)
#     print(res)
#
#     print(type(res))
