# -*- coding: utf-8 -*-

"""
@Project : didabox 
@File    : check.py
@Date    : 2023/10/31 18:03:44
@Author  : zhchen
@Desc    : 
"""
import time

from requests import Response

from didabox.utils import MidBox


class CheckBox(MidBox):

    def check_cookie(self) -> Response:
        """检测cookie是否失效, 失效状态码!=200"""
        # cookie失效例子👇🏻
        # <Response [401]>
        # {"errorId":"w0ht4nm1@ctw6","errorCode":"user_not_sign_on","errorMessage":"user_not_sign_on","data":null}
        params = {'from': str(int(time.time()) * 1000)}
        response = self.req.get('https://api.dida365.com/api/v2/column', params=params)
        return response
