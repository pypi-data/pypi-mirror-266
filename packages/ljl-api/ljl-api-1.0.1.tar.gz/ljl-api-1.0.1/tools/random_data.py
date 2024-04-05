# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: random_data.py
@date: 2022/09/04 14:32
"""

# 定义方法和关键字RandomString绑定的方法
import random

from faker import Faker

fake = Faker("zh_CN") # 默认是英文的，初始化成中文的

def random_str(send_request,length,content):
    res = random.choices(content,k=int(length))
    return "".join(res)

# 定义生成随机数的方法
def random_int(send_request,start,end): # 参数都是字符串
    res = random.randint(int(start),int(end))
    return str(res) # 返回值也需要是一个字符串

def random_phone(send_request):
    return f"{fake.phone_number()}"