# -*- coding: utf-8 -*-

"""
@Project : didabox 
@File    : request.py
@Date    : 2023/12/1 10:28:52
@Author  : zhchen
@Desc    : 
"""
import requests
from requests import Response


class Request:
    def __init__(self, cookies: dict, tz: str, headers=None):
        """
        简化请求
        :param cookies:
        :param tz: 时区
        :param headers:
        """
        self.cookies = cookies
        self.tz = tz
        self.headers = headers or {
            'authority': 'api.dida365.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            'hl': 'zh_CN',
            'origin': 'https://dida365.com',
            'pragma': 'no-cache',
            'referer': 'https://dida365.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'x-tz': self.tz,
        }

    def get(self, url, params, **kwargs) -> Response:
        return requests.get(url, params=params, cookies=self.cookies, headers=self.headers, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return requests.post(url, data, json, cookies=self.cookies, headers=self.headers, **kwargs)
