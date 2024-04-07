# -*- coding: utf-8 -*-

"""
@Project : didabox 
@File    : main.py
@Date    : 2023/12/1 10:16:44
@Author  : zhchen
@Desc    : 
"""
from requests import Response

from didabox.check import CheckBox
from didabox.info import InfoBox
from didabox.request import Request
from didabox.task import TaskBox
from didabox.login import LoginBox


class DidaBox:
    def __init__(self, cookies: dict, headers=None):
        self.req = Request(cookies=cookies, tz='Asia/Shanghai', headers=headers)
        self.check_box = CheckBox(self)
        self.task_box = TaskBox(self)
        self.login_box = LoginBox(self)
        self.info_box = InfoBox(self)

    # == 账号维度 ==
    def check_cookie(self) -> Response:
        """检测cookie是否过期"""
        return self.check_box.check_cookie()

    def sign_on(self, username, password) -> Response:
        """
        账号密码登录, 登录完成后自动更新cookie
        :param username: 账号
        :param password: 密码
        :return:
        """
        return self.login_box.sign_on(username, password)

    # -- 账号维度 --

    # == 清单任务维度 ==
    def base_info(self):
        """清单的基本信息"""
        return self.info_box.base_info()

    def add_simple_task(self, project_id: str, title: str, content: str, trigger_time: str) -> Response:
        """
        添加简单的任务
        :param project_id: 清单id
        :param title: 任务标题
        :param content: 任务内容
        :param trigger_time: 触发时间, 准时触发. 格式: %Y-%m-%d %H:%M:%S
        :return:
        """
        return self.task_box.add_reminders_task(project_id, title, content, trigger_time)

    def get_completed_tasks(self, to_date, from_date: str = '', limit: int = 50) -> Response:
        """
        获取已完成的任务
        :param to_date: 格式 2024-03-28 00:57:26
        :param from_date:
        :param limit:
        """
        return self.task_box.all_completed(from_date=from_date, to_date=to_date, limit=limit)

    def search(self, keywords: str) -> Response:
        """根据关键词查询相关任务"""
        return self.task_box.search_all(keywords)
    # -- 清单任务维度 --
