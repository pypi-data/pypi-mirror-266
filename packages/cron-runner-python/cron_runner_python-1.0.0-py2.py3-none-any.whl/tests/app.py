# -*- coding: utf-8 -*-
"""
@File    : app.py
@Date    : 2024-04-04
"""
import logging
# pip install requests flask
import time
import random
from flask import Flask

from cron_runner import CronRunner, CronRunnerContext

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

cron_runner_logger = logging.getLogger('cron-runner')
cron_runner_logger.setLevel(logging.INFO)
cron_runner_logger.addHandler(logging.StreamHandler())

app = Flask(__name__)

# 配置
runner = CronRunner(app)
runner.set_host('http://127.0.0.1:8082')


@runner.add_task('run_job')
def run_job_1(ctx: CronRunnerContext):
    ctx.log("data: {}".format(ctx))

    # cost some time
    time.sleep(random.randint(0, 10))

    # raise a runtime exception
    if random.randint(0, 1) > 0.5:
        a = 1 / 0

    ctx.log('run_job complete')


# 模拟耗时任务
@runner.add_task
def run_job_2(ctx: CronRunnerContext):
    ctx.log("data: {}".format(ctx))

    time.sleep(5)
    ctx.running()

    ctx.log('run_job complete')


if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)
