# -*- coding: utf-8 -*-

"""
@Project : didabox 
@File    : info.py
@Date    : 2024/3/29 13:11:39
@Author  : luke
@Desc    : 
"""

from requests import Response

from didabox.utils import MidBox


class InfoBox(MidBox):

    def base_info(self) -> Response:
        """ 清单的基本信息:
        * 清单: 清单名称、清单id
        * 清单文件夹:
        * 过滤器:
        * 标签:
        * 未完成的任务:
        * ...
        """
        response = self.req.get('https://api.dida365.com/api/v2/batch/check/0', params={})
        return response
