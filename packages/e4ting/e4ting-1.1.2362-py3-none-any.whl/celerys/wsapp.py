#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    Add By :e4ting chendejun@antiy.cn 2022-09-09 10:57:41
    docker run --rm -ti --net airflow_default -u root --env-file .env --name threat.data -v /home/aliyun/:/code -w /code e4ting/airflow:2.2.2 bash -c "celery -A apps.app worker -P gevent -Q data.threat"
"""
import sys,os
from pdb import set_trace as strace
from traceback  import format_exc as dumpstack

import os
import sys

from celery import Celery,platforms
import functools

platforms.C_FORCE_ROOT = True

# include:导入指定的任务模块
# 创建 app，并没有直接指定 broker(消息中间件来接收和发送任务消息) 和 backend(存储结果)。而是在配置文件中。
app = Celery(
    'celery',
    include=[
        "celerys.tasks.server",
    ],
    broker = 'redis://redis.com/7',
    backend = 'redis://redis.com/7',
    broker_url = 'redis://redis.com/7',
    #backend(存储worker执行的结果) 可以存储在不同的db
    result_backend = 'redis://redis.com/7',
    #设置时间参照，不设置默认使用的UTC时间
    timezone = 'Asia/Shanghai',
    #指定任务的序列化
    task_serializer='json',
    #指定执行结果的序列化
    result_serializer='json',
    #配置每个任务的最多执行时间，超过则杀掉  这个时间需要经过测试再调整
    task_time_limit=60,
    # 配置结果在redis中存放的时间，单位为s，存储10分钟吧，后续再调
    result_expires=30,
    worker_redirect_stdouts = False,
    worker_hijack_root_logger = False,
)

def WebsocketCeleryApp():
    def wraps(func):
        @app.task(name=func.__name__)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            return res
        return wrapper
    return wraps
