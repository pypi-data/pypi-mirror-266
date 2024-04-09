#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    [模块名]
    Add By :e4ting e4ting@gmail.com 2023-03-07 14:19:59
"""
import sys,os
import json,time
from pdb import set_trace as strace
from traceback  import format_exc as dumpstack

from functools  import partial

# from modules.common import util
# from modules.common.utilrecord import save_7niu_api
# from modules.common.utilmongo  import db
# from celery_task.py_tasks.python import get_miner_devs
from celerys.tasks.task import *
from celerys.app import app

# class ACelery(object):
#     # async 异步调用
#     def apply_async(self, func, *args, **kwargs):
#         return func.apply_async(args=args, kwargs=kwargs)

#     def __getattr__(self, func):
#         assert hasattr(python, func), "未定义此函数"
#         return partial(self.apply_async, getattr(python, func))

# class BCelery(object):
#     # block 阻塞调用
#     def __init__(self, second=10):
#         self.timeout = second

#     def apply_async(self, func, *args, **kwargs):
#         if self.timeout is None:
#             return func.apply_async(args=args, kwargs=kwargs).get()
#         return func.apply_async(args=args, kwargs=kwargs).get(self.timeout)

#     def __getattr__(self, func):
#         assert hasattr(python, func), "未定义此函数"
#         return partial(self.apply_async, getattr(python, func))

class TaskTemplate(object):
    def __init__(self, second=10, queue=None):
        self.queue = queue

        # 阻塞多少秒返回
        self.timeout = second

# 单词是匿名的意思
class Anon(TaskTemplate):
    # async 异步调用，完全不关心集群中是否有节点执行此任务
    def apply_async(self, func, *args, **kwargs):
        if self.queue is None:
            return globals()["app"].send_task(func, args=args, kwargs=kwargs)
        return globals()["app"].send_task(func, args=args, kwargs=kwargs, queue=self.queue)

    def __getattr__(self, func):
        return partial(self.apply_async, func)


class Async(TaskTemplate):
    # async 异步调用
    def apply_async(self, func, *args, **kwargs):
        if self.queue is None:
            return func.apply_async(args=args, kwargs=kwargs)
        return func.apply_async(args=args, kwargs=kwargs, queue=self.queue)

    def __getattr__(self, func):
        assert func in globals(), "未定义此函数"
        return partial(self.apply_async, globals()[func])


class Block(Async):
    # block 阻塞调用

    def run(self, func, *args, **kwargs):
        if self.timeout is None or self.timeout <= 0:
            return self.apply_async(func, *args, **kwargs).get()
        return self.apply_async(func, *args, **kwargs).get(self.timeout)

    def __getattr__(self, func):
        assert func in globals(), "未定义此函数"
        return partial(self.run, globals()[func])
