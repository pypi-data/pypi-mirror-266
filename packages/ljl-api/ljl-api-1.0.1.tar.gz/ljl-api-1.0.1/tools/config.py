# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: config.py
@date: 2022/08/28 13:27
"""
import configparser
import os
from tools.log import Logger

class Config():
    config = None

    def __init__(self):
        if self.config is None:
            __class__.config = configparser.ConfigParser() # 初始化解析器
            self.fille_path = os.path.join(os.getcwd(),f"{os.environ.get('env')}.ini")
            Logger().info(f"加载配置文件：{self.fille_path}")
            self.config.read(self.fille_path, encoding="utf-8")



    def get_url(self,app):
        try:
            return self.config.get("url",app)
        except:
            Logger().error(f"配置文件{self.fille_path}中，不存在对应的值。section: url,option: {app}")
            raise

    def get_db(self,app):
        try:
            db_config = dict(self.config.items(f"{app}_db"))
            db_config["port"] = int(db_config["port"])
            return db_config
        except:
            Logger().error(f"配置文件{self.fille_path}中，不存在对应的值。section: url,option: {app}")
            raise
    def get_root_path(self):
        root_path = self.config.get("base","root_path")
        root_path = root_path or os.getcwd()
        return root_path


