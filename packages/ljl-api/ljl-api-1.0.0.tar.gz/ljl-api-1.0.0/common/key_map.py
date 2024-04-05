# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: key_map.py
@date: 2022/09/04 14:32
"""
from tools.assert_methods import json_assert, respose_assert, batch_assert
from tools.common_methods import get_var, mysql_tools, save_file
from tools.post_process_methods import json_excutor
from tools.random_data import random_str, random_int, random_phone

# 添加关键字和对应方法之间的绑定关系
key_maps = {
    "RANDOMSTRING":random_str,
    "RANDOMINT":random_int,
    "PHONE":random_phone,
    "JSONEXCUTOR":json_excutor,
    "GETVAR":get_var,
    "MYSQL":mysql_tools,
    "JSONASSERT":json_assert,
    "RESPONSEASSERT":respose_assert,
    "BATCHASSERT":batch_assert,
    "SAVEFILE":save_file,
}
