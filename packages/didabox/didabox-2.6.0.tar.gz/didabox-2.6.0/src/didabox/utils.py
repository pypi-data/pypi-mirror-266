# -*- coding: utf-8 -*-

"""
@Project : didabox 
@File    : utils.py
@Date    : 2023/12/1 9:52:23
@Author  : zhchen
@Desc    : 
"""
import random
import string
from datetime import datetime

import pytz

from didabox.request import Request


class Tools:

    @staticmethod
    def random_str(num=24) -> str:
        # 16进制字符集
        hex_chars = string.hexdigits[:-6]  # 去除字母大小写重复部分
        # 生成随机的16进制字符串
        random_hex_string = ''.join(random.choice(hex_chars) for _ in range(num))
        return random_hex_string

    @staticmethod
    def random_int(num=13) -> int:
        # 生成一个13位随机数字
        random_number = ''.join(str(random.randint(0, 9)) for _ in range(num))
        return int(random_number)

    def shanghai2utc(self, _date: str) -> str:
        """上海时区转成utc时区"""
        dt = datetime.fromisoformat(_date)
        original_timezone = pytz.timezone('Asia/Shanghai')
        dt = original_timezone.localize(dt)
        target_timezone = pytz.timezone('UTC')
        converted_time = dt.astimezone(target_timezone)
        return converted_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    @staticmethod
    def utc2str(_date: str) -> str:
        """[%Y-%m-%dT%H:%M:%S.%f%z]格式转成[%Y-%m-%d %H:%M:%S]格式"""
        dt = datetime.fromisoformat(_date)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def str2utc(_date: str) -> str:
        """[%Y-%m-%d %H:%M:%S]格式转成[%Y-%m-%dT%H:%M:%S.%f%z]格式"""
        dt = datetime.strptime(_date, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    @staticmethod
    def now():
        now = datetime.now()
        return now.strftime("%Y-%m-%dT%H:%M:%S.%f%z")


class MidBox(Tools):
    def __init__(self, box):
        from didabox.main import DidaBox
        self.box: DidaBox = box
        self.req: Request = self.box.req
