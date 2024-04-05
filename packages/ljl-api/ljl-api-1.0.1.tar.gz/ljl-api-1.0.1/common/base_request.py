# -*- coding:utf-8 -*-
"""
@author: xuepl
@file: base_request.py
@date: 2022/08/28 16:32
"""
from common.descriptions import UrlDesc, MethodDesc, ParamsDesc, DataDesc, JsonDesc, HeadersDesc, FilesDesc, ConfigDesc


class BaseRequest():
    app = MethodDesc()
    url = UrlDesc()
    method = MethodDesc()
    params = ParamsDesc()
    data = DataDesc()
    json = JsonDesc()
    headers = HeadersDesc()
    files = FilesDesc()
    config = ConfigDesc()


