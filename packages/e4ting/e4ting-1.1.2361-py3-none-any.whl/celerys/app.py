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

# from celerys.celeryapp import app,BaseCeleryApp

from celery import Celery,platforms
from celery_once import QueueOnce
import functools

# from kombu import Exchange, Queue

platforms.C_FORCE_ROOT = True

# include:导入指定的任务模块
# 创建 app，并没有直接指定 broker(消息中间件来接收和发送任务消息) 和 backend(存储结果)。而是在配置文件中。
app = Celery(
    'celery',
    include=[
        "celerys.tasks.task",
    ],
)

class celeryconfig():
    # 详细配置查看官方文档： http://docs.celeryproject.org/en/latest/userguide/configuration.html

    #broker(消息中间件来接收和发送任务消息)
    broker_url = 'redis://redis.com/7'
    #backend(存储worker执行的结果) 可以存储在不同的db
    result_backend = 'redis://redis.com/7'

    #设置时间参照，不设置默认使用的UTC时间
    timezone = 'Asia/Shanghai'
    #指定任务的序列化
    task_serializer='json'
    #指定执行结果的序列化
    result_serializer='json'
    #配置每个任务的最多执行时间，超过则杀掉  这个时间需要经过测试再调整
    task_time_limit=60
    # 配置结果在redis中存放的时间，单位为s，存储10分钟吧，后续再调
    result_expires=30

    worker_redirect_stdouts = False

    ONCE = {
        "backend":"celery_once.backends.Redis",
        'settings_prefix': 'once',
        "settings":{
            "url":"redis://redis.com/7",
            "default_timeout":60
        }
    }
    once_backend = 'celery_once.backends.Redis'
    once_redis_url = 'redis://redis.com/7'
    once_default_timeout = 60

    ONCE_BACKEND = 'celery_once.backends.Redis'
    ONCE_REDIS_URL = 'redis://redis.com/7'
    ONCE_DEFAULT_TIMEOUT = 60


    # 这个是为了兼容go序列化
    task_serializer = "json"
    # accept_content='json'
    # result_serializer='json'
    enable_utc = True
    task_protocol = 1

    # 时间间隔用质数分开，减少同时触发的概率
    beat_schedule = {
            'flush-iptables':{
                    'task': 'flush_iptables', # 这里不要写全路径
                    'schedule': 61,
            },
            'bot-keepalive':{
                    'task': 'botnet_ws_keepalive', # 这里不要写全路径
                    'schedule': 59,
            },
            'bot-refresh-online':{
                    'task': 'refresh_online', # 刷新数据库中节点的在线状态
                    'schedule': 307,
            },
        }


# 通过Celery 实例加载配置模块，在celeryconfig中声明各种配置
app.config_from_object(celeryconfig)

def BaseCeleryApp():

    def wraps(func):
        @app.task(base=QueueOnce, name=func.__name__)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            return res
        return wrapper

    return wraps
