# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: common_methods.py
@date: 2022/09/18 11:48
"""
import os

import jsonpath

from common.custom_exception import KeysExcutorFailed
from tools.log import Logger
from tools.mysql_tools import MySQLTool


def get_var(send_request,var_name):
    '''
    令牌
    用户信息[0].login_name
    用户信息.login_name
    用户信息[0]['login_name']
    用户信息[0]["login_name"]
    :param send_request:
    :param var_name:
    :return:
    '''
    json_path = None
    if "." in var_name or "[" in var_name:
        one = var_name.find("[")
        two = var_name.find(".")
        if one == -1:
            index = two
        elif two == -1:
            index = one
        else:
            index = min(one,two)
        name = var_name[:index]
        json_path = "$" + var_name[index:]
    else:
        name = var_name
    local_vars = send_request.local_vars
    if name not in local_vars:
        Logger().error(f"变量名错误：{var_name}")
        raise KeysExcutorFailed
    value = local_vars[name]
    if json_path is None:
        return value
    else:
        return jsonpath.jsonpath(value,json_path)[0]

# 用户信息,mall,select login_name,password_md5 from tb_newbee_mall_user limit 10;
# *("用户信息","mall","select login_name","password_md5 from tb_newbee_mall_user limit 10;")
# app = "mall" args = ("用户信息","select login_name","password_md5 from tb_newbee_mall_user limit 10;")
def mysql_tools(send_request,app,*args):
    var_name=None
    sql = None
    one = args[0].strip()
    if len(one) > 6 and one[:6] in ["DELETE","UPDATE","INSERT","SELECT"]:
        sql = ",".join(args)
    else:
        var_name=args[0]
        sql = ",".join(args[1:])
    db_config = send_request.base_request.config.get_db(app)
    if sql[:6].upper() == "SELECT" and var_name is not None:
        with MySQLTool(**db_config) as db:
            res = db.query(sql)
            Logger().debug(f"sql查询成功：{res}")
            send_request.local_vars[var_name] = res
    else:
        with MySQLTool(**db_config) as db:
            db.update(sql)

# 把响应正文的数据，写入到文件中
def save_file(send_request,filepath):
    root_path = send_request.base_request.config.get_root_path()
    dir_name,file_name = os.path.split(filepath) # 获取文件夹路径和文件名字
    dir_path = os.path.join(root_path,dir_name) # 获取文件夹路径
    os.makedirs(dir_path) # 创建文件夹
    filepath = os.path.join(root_path,filepath)
    with open(filepath,"rb") as f:
        f.write(send_request.base_response.response_body_content)


