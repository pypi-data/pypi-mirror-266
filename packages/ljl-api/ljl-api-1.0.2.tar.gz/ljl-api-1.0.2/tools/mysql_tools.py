# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: mysql_tools.py
@date: 2022/08/28 14:18
"""

import pymysql


class MySQLTool():
    def __init__(self, host, user, password, db, port=3306, charset="utf8"):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = port
        self.charset = charset

    def __connect(self):
        # 建立数据库链接
        self.__conn = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.db,
            port=self.port,
            charset=self.charset,
            cursorclass=pymysql.cursors.DictCursor
        )
        # 创建游标
        self.__cursor = self.__conn.cursor()

    def __enter__(self):
        '''
        进入上下文管理器的入口方法
        :return:
        '''
        self.__connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        上下文管理器的退出方法
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        '''
        self.__close()

    def query(self, sql):
        '''
        查询
        :param sql: sql语句
        :return:
        '''
        self.__cursor.execute(sql)  # 执行sql语句
        res = self.__cursor.fetchall()  # 获取所有的查询结果
        return res

    def update(self, sql):
        '''
        增删改
        :param sql:sql语句
        :return:
        '''
        effect_row = self.__cursor.execute(sql)  # 执行sql语句
        self.__conn.commit()  # 增删改必须要提交，不然不生效
        return effect_row

    def __close(self):
        self.__cursor.close()  # 关闭游标
        self.__conn.close()  # 关闭数据库链接

if __name__ == '__main__':

    with MySQLTool(host="api.xuepl.com.cn",password="SongLin2021",user="root",db="mall") as db:
        print(db.update("select login_name,password_md5 from tb_newbee_mall_user limit 10;"))
        # print(db.update("update tb_newbee_mall_user set password_md5='e10adc3949ba59abbe56e057f20f883e' where user_id=17;"))
