# encoding: utf-8
"""
@version: ??
@author: lizheao
@contact: lizheao@wecash.net
@software: PyCharm
@file: httptool.py
@time: 下午5:58
"""
import aiohttp


class ClientSession(aiohttp.ClientSession):
    def request(self, method, url, **kwargs):
        return self._request(method=method, url=url, **kwargs)
