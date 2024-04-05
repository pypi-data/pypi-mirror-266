# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: keys_driver.py
@date: 2022/09/04 13:13
"""
from common.custom_exception import KeysExcutorFailed
from common.key_map import key_maps
from tools.log import Logger


class KeysDriver():

    def __init__(self,send_request,value):
        """
        包含关键字的字符串
        :param value:
        """
        self.send_request = send_request
        self.value = value
        self.key_replace()

    def keys_parser(self,value):
        '''
        关键字特征：$__开头  )$结尾
        $__PHONE()$
        $__RandomString(6,abcdefghijklmn)$
        $__RandomInt(10,20)$
        $__RandomString($__RandomInt(10,20)$,abcdefgh$ijklmn)$
        :param value:
        :return: 返回关键字组成的列表。普通关键字，直接放到列表中。嵌套关键字，把最外层的关键字放到列表中
        '''
        length = len(value) # 字符串的长度
        __keys = [] # 存放关键字的列表
        start = -1 # 关键字的起始索引，如果是-1则表示，未遇到过关键字
        flag = 0 # 作为关键字出现时，开始和结束是否是成对出现的标志
        for i in range(length): # 使用索引去遍历整个字符串
            if value[i] == "$":  # 说明，可能遇到了关键字的开始或者是结束标志
                # 判断关键字的起始
                if i + 2 < length and value[i:i+3] == "$__":
                    flag -= 1 # 遇到关键字起始，flag值减去1
                    # 记录一下，关键字的起始索引
                    if start < 0: # 如果start的值为-1.说明是第一次遇到关键字的起始索引（可能会涉及到关键字嵌套的问题）
                        start = i
                elif i-1 >= 0 and value[i-1:i+1] == ")$": # 判断关键字的结束
                    flag += 1 # 遇到关键字的结束，flag值就加上1
                    if flag == 0 and start >= 0: # flag等于0的时候，说明关键字起始和结束标记成对
                        __keys.append(value[start: i+1])
                        start = -1 # 重置关键字开始的索引
        return __keys # 返回关键字列表

    def key_run(self,key):
        '''
        关键字嵌套
        :param key:
        :return:
        '''
        # 判断关键字中，是否存在嵌套关系
        if "$__" in key[3:]:
            # 先处理内层关键字
            inner_keys = self.keys_parser(key[3:-1])
            for i_k in inner_keys:
                res = self.key_run(i_k) # 使用递归实现，内层关键字多层嵌套执行
                if res is not None and isinstance(res, str):
                    key = key.replace(i_k,res,1) # 使用内层关键字的执行结果，替换掉对应的内层关键字
        key_name = key[3:key.find("(")].strip().upper() # 获取关键字的名称
        key_args = key[key.find("(")+1:-2] # 获取关键字参数

        # 获取对应关键字方法的名字
        try:
            if key_args == "":
                return key_maps[key_name](self.send_request)
            else:
                return key_maps[key_name](self.send_request,*key_args.split(","))
        except KeyError:
            Logger().error(f"关键字名称：{key_name} 未定义")
            # print(f"关键字名称：{key_name} 未定义")
            return
        except KeysExcutorFailed:
            Logger().error(f"关键字{key},执行失败")
            # print(f"关键字{key},执行失败")
            return
        except AssertionError:
            raise

    def key_replace(self):
        # 解析数据中的关键字
        keys = self.keys_parser(self.value)
        for k in keys:
            res = self.key_run(k)  # 所有的关键字，执行结果必须是字符串。
            if res is not None and isinstance(res,str): # 如果返回值，不为空，则实现替换
                self.value = self.value.replace(k,res,1) # 使用关键字的执行结果，原字符串中对应的关键字






if __name__ == '__main__':

    s = "$__RandomString(8,012345$6789abcdefghijklmn)$需要用到$__RandomString(13,abcdefgh$ijklmn)$随机数据：$__RandomString(8,012345$6789abcdefghijklmn)$：用完了$__RandomString(8,012345$6789abcdefghijklmn)$"
    kd = KeysDriver(s)
    print(kd.value)

