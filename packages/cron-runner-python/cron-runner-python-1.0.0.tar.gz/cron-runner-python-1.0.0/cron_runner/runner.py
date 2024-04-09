# -*- coding: utf-8 -*-
"""
@File    : core.py
@Date    : 2024-04-07
"""

from flask import request, jsonify

from cron_runner import config, context
from cron_runner.task_runner import TaskRunner, SendMessageRunner
from cron_runner.log import logger

class CronRunner(object):
    def __init__(self, app):
        self.app = app
        self.host = None

        self.tasks = {}
        self.task_runner = None
        self.task_report_runner = None

        # auto
        self._register_router()

    def set_host(self, host):
        self.host = host

    def add_task(self, func_or_name, name=None):
        """
        add task func
        :param func_or_name:
        :param name:
        :return:
        """
        if callable(func_or_name):
            name = name or func_or_name.__name__
            self.tasks[name] = func_or_name
        else:
            this = self

            def inner(func):
                this.tasks[func_or_name] = func

            return inner

    def _register_router(self):
        self.app.add_url_rule(rule=config.API_START_TASK, endpoint=None, view_func=self._start_task, methods=['POST'])

    def _start_task(self):
        # 1、接收线程
        data = request.get_json()
        logger.info('receive data: %s', data)

        task_name = data.get('taskName')
        ctx = context.CronRunnerContext(self.host, data)

        task_func = self.tasks[task_name]

        # 2、执行线程
        if not self.task_runner:
            self.task_runner = TaskRunner()
            self.task_runner.start()

        # 3、汇报线程
        if not self.task_report_runner:
            self.task_report_runner = SendMessageRunner(config.DEFAULT_CRON_ADMIN_HOST + config.API_REPORT_TASK_STATUS)
            self.task_report_runner.start()

        ctx.set_task_report(self.task_report_runner)

        self.task_runner.submit_task(task_func, ctx)

        return jsonify({'msg': 'success', 'data': None, 'code': 0})
