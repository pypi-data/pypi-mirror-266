# -*- coding: utf-8 -*-

"""
@Project : didabox 
@File    : task.py
@Date    : 2023/10/31 13:42:42
@Author  : zhchen
@Desc    : 
"""
from urllib.parse import urlencode

from requests import Response

from didabox.utils import MidBox


class TaskBox(MidBox):
    def _task_api(self, data: dict) -> Response:
        response = self.req.post('https://api.dida365.com/api/v2/batch/task', json=data)
        return response

    def add_reminders_task(self, project_id: str, title: str, content: str, trigger_time: str) -> Response:
        """添加任务"""
        trigger_time = self.str2utc(trigger_time)
        json_data = {
            'add': [
                {
                    'items': [],
                    'reminders': [
                        {
                            'id': self.random_int(),
                            'trigger': 'TRIGGER:PT0S',
                        },
                    ],
                    'exDate': [],
                    'dueDate': None,
                    'priority': 0,
                    'isAllDay': False,
                    'repeatFlag': None,
                    'progress': 0,
                    'assignee': None,
                    'sortOrder': -self.random_int(),
                    'startDate': self.shanghai2utc(trigger_time),
                    'isFloating': False,
                    'status': 0,
                    'projectId': project_id,
                    'kind': None,
                    'createdTime': self.shanghai2utc(self.now()),
                    'modifiedTime': self.shanghai2utc(self.now()),
                    'title': title,
                    'tags': [],
                    'timeZone': self.box.tz,
                    'content': content,
                    'id': self.random_str(),
                },
            ],
            'update': [],
            'delete': [],
            'addAttachments': [],
            'updateAttachments': [],
            'deleteAttachments': [],
        }
        return self._task_api(json_data)

    def all_completed(self, from_date='', to_date='', limit=50):
        """
        查询已完成的task
        :param from_date: 格式 2024-03-28 00:57:26
        :param to_date:
        :param limit:
        """
        params = {
            "from": from_date,
            "to": to_date,
            "limit": str(limit)
        }
        # 冒号不能转义 (= =)
        encoded_params = urlencode(params, safe=":")
        response = self.req.get("https://api.dida365.com/api/v2/project/all/completed/?" + encoded_params, params={})
        return response

    def search_all(self, keyword: str):
        """搜索"""
        params = {'keywords': keyword}
        response = self.req.get('https://api.dida365.com/api/v2/search/all', params=params)
        return response
