# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: excel_tools.py
@date: 2022/09/04 15:58
"""
import os

import xlrd

from tools.config import Config

'''
给定一个excel的相对路径，
1、使用root_path 和excel的相对路径进行拼接
2、读取excel所有sheet中的数据，按照顺序，放入一个列表中
3、每条用用例数据，都是一个字典
'''
def read_excel(file_path):
    root_path = Config().get_root_path() # 获取root_path
    # root_path = "E:\\workspace\\edu\\auto_api_2207B"
    file_path = os.path.join(root_path,file_path) # 获取excel文件的绝对路径
    excel = xlrd.open_workbook(file_path) # 打开excel
    sheets = excel.sheets() # 获取到excel中，所有的sheet
    case_list = []
    ids = []
    for s in sheets: # 遍历每个一个sheet
        rows = s.nrows # 获取每个sheet中，有数据的行数
        if rows < 3:
            continue
        keys = s.row_values(1) # 读取excel中，第二行数据，作为字典的key
        for n in range(2,rows):
            row = s.row_values(n) # 把数据列，每行的数据，读出来
            case = dict(zip(keys,row)) # 把每行内容，转换成一个python字典
            print(case["title"])
            if case["is_run"].strip() == "否" or case["title"] == "": # 如果用例不需要运行，则不放入列表中
                continue
            ids.append(case["title"]) # 用例标题，加入ids列表中
            case_list.append(case)# 用例数据放入case_list列表中
    return ids,case_list

def scan_excels(file_path):
    excel_files = []
    files = os.listdir(file_path)
    for f in files:
        file = os.path.join(file_path,f)
        if os.path.isdir(file) and f not in [".pytest_cache","venv",".idea",".git","__pycach__"]:
            res = scan_excels(file)
            excel_files.extend(res)
        elif os.path.isfile(file) and file.endswith(".xls"):
            excel_files.append(file)
    return excel_files


def get_cases():
    root_path = Config().get_root_path()
    excel_files = scan_excels(root_path)
    ids = []
    cases=[]
    for f in excel_files:
        i,cs = read_excel(f)
        ids.extend(i)
        cases.extend(cs)
    return ids,cases


if __name__ == '__main__':
    print(read_excel("ceshi.xls"))


