# -*- coding: utf-8 -*-
"""
@File    : task_runner.py
@Date    : 2024-04-08
"""

import queue
import threading
import traceback

import requests

from cron_runner import config
from cron_runner.log import logger
from cron_runner.version import VERSION

try:
    from cron_runner.context import CronRunnerContext
except ImportError:
    pass


class SendMessage(object):
    def __init__(self, taskLogId, data) -> None:
        self.taskLogId = taskLogId
        self.data = data

    def to_dict(self):
        return {
            'taskLogId': self.taskLogId,
            'data': self.data,
        }

    def __str__(self) -> str:
        return "<{name}: {data}>".format(
            name=self.__class__.__name__,
            data=self.to_dict()
        )


class TaskRunner(threading.Thread):
    task_queue = queue.Queue()

    def run(self):
        logger.info('runner thread start')

        while True:
            (task, ctx) = self.task_queue.get()

            # 等待数量
            ctx.set_wait_task_count(self.task_queue.qsize())

            logger.info('get new task: %s', ctx.task_log_id)
            task(ctx)

    def submit_task(self, task, ctx):
        self.task_queue.put((self.run_task_wrap(task), ctx), block=False)

    def run_task_wrap(self, func):
        # type: (callable)->callable
        def run_task(ctx):
            # type: (CronRunnerContext)->None
            """
            :param ctx:
            :return:
            """

            ctx.run_start()

            try:
                func(ctx)
            except Exception as e:
                ctx.log(traceback.format_exc())
                ctx.run_error()
            else:
                ctx.run_success()

        return run_task


class SendMessageRunner(threading.Thread):
    task_queue = queue.Queue()
    batch_size = 16

    def __init__(self, host):
        super().__init__()
        self.host = host

    def run(self):
        logger.info('status report thread start')

        while True:
            lst = []
            # block wait
            message = self.task_queue.get()
            lst.append(message)
            # logger.info('message: %s', message)

            # batch message
            while self.task_queue.qsize() > 0:
                message = self.task_queue.get()
                # logger.info('message: %s', message)
                lst.append(message)

                if len(lst) >= self.batch_size:
                    break

            # merge message {taskLogId, message}
            merged_message = {}
            for msg in lst:
                merged_msg = merged_message.get(msg['taskLogId']) or {}

                # merge log
                merged_logs = []
                merged_logs.extend(merged_msg.get('logs', []))
                merged_logs.extend(msg['logs'])

                # last status
                merged_msg = {
                    'taskLogId': msg['taskLogId'],
                    'status': msg['status'],
                    'logs': merged_logs,
                }

                merged_message[msg['taskLogId']] = merged_msg
            # logger.info("merged_message: %s", merged_message)

            # send message
            merged_list = [
                {
                    'taskLogId': msg['taskLogId'],
                    'status': msg['status'],
                    'text': '\n'.join(msg['logs']),
                } for msg in merged_message.values()
            ]

            logger.info('send message: %s', merged_list)

            # runner version
            headers = {
                'X-Runner-Version': VERSION
            }

            try:
                requests.post(self.host, headers=headers, json=merged_list, timeout=3)
            except Exception as e:
                traceback.print_exc()

    def add_message(self, message: SendMessage):
        self.task_queue.put(message, block=False)
