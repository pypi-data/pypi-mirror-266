# -*- coding:utf-8 -*-
"""
@author:李景龙
@file: setup.py.py
@date: 2024/04/04 20:47
"""
from distutils.core import setup

setup(
    name="ljl-api",   # 这里是pip项目发布的名称
    version="1.0.1",
    keywords=["init", "auto-test"],  # pip 官网搜索关键字
    description="to simplify auto test",   # 简单描述
    long_description="A init package,to simplify develope auto test",  # 详细描述
    license="MIT Licence",

    url="https://git.code.tencent.com/2024111/lijl.git",
    author="ljl",
    author_email="1316597471@qq.com",
    packages=["tools", 'common'],
    platforms="python",
    install_requires=[
        'allure-pytest==2.9.45',
        'configparser==5.2.0',
        'Faker==13.3.4',
        'jsonpath==0.82',
        'PyMySQL==1.0.2',
        'pytest==7.1.1',
        'requests==2.27.1',
        'xlwt==1.3.0',
        'xlrd==2.0.1'
    ]

)


