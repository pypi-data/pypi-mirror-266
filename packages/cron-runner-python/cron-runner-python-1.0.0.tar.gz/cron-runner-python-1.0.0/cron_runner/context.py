# -*- coding: utf-8 -*-
"""
@File    : context.py
@Date    : 2024-04-07
"""
import json
from datetime import datetime
import requests

from cron_runner import config
from cron_runner.log import logger
from cron_runner.task_runner import SendMessage


class TaskStatusEnum(object):
    # == = 启动阶段 == =
    # 启动失败
    START_ERROR = 1
    # 启动成功
    START_SUCCESS = 2

    # === 运行阶段 == =
    # 开始运行
    RUN_START = 3
    # 运行中
    RUNNING = 4

    # == = 结束阶段 == =
    # 运行成功
    RUN_SUCCESS = 5

    # 运行失败
    RUN_ERROR = 6


class CronRunnerContext(object):
    def __init__(self, host, data):
        self.host = host or config.DEFAULT_CRON_ADMIN_HOST
        self.data = data
        self.status = None
        self.logs = []
        self.wait_task_count = 0
        self.reporter = None

    def log(self, msg):
        self.status = TaskStatusEnum.RUN_START
        self._log(msg)

    def _log(self, msg):
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        text = '[{}] {}'.format(time, msg)
        logger.info(text)
        self.logs.append(text)
        self.report()

    def set_wait_task_count(self, value):
        self.wait_task_count = value

    def set_task_report(self, reporter):
        self.reporter = reporter

    @property
    def task_log_id(self):
        return self.data['taskLogId']

    def run_start(self):
        self.status = TaskStatusEnum.RUN_START
        self._log('===任务开始运行===')

    def running(self):
        self.status = TaskStatusEnum.RUNNING

    def run_error(self):
        self.status = TaskStatusEnum.RUN_ERROR
        self._log('===任务运行失败===')

    def run_success(self):
        self.status = TaskStatusEnum.RUN_SUCCESS
        self._log('===任务运行成功===')

    def report(self):
        data = {
            'taskLogId': self.task_log_id,
            'status': self.status,
            'logs': self.logs.copy(),
        }

        self.logs.clear()

        self.reporter.add_message(data)

    def to_dict(self):
        return {
            # 'host': self.host,
            'status': self.status,
            'data': self.data,
        }

    def __str__(self) -> str:
        return "<{name}: {data}>".format(
            name=self.__class__.__name__,
            data=self.to_dict()
        )
