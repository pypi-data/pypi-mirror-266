# -*- coding: utf-8 -*-

"""
@Project : didabox 
@File    : login.py
@Date    : 2023/12/1 11:29:05
@Author  : zhchen
@Desc    : 
"""
from didabox.utils import MidBox


class LoginBox(MidBox):

    def sign_on(self, username, password):
        """账号密码登录接口"""
        json_data = {
            "username": username,
            "password": password,
        }
        response = self.req.post("https://api.dida365.com/api/v2/user/signon?wc=true&remember=true", json=json_data)
        self.req.cookies = dict(response.cookies)
        return response

