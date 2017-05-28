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
    async def request(self, method, url, **kwargs):
        _rep = await self._request(method=method, url=url, **kwargs)
        return _rep
