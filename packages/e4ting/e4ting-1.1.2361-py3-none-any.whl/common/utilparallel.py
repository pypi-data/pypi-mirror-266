#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    高并发模块
    Add By : cdj <e4ting@qq.com> 2021-09-06 12:25:00
"""

import gevent
from gevent import monkey, Greenlet,core
monkey.patch_all()
from gevent.pool import Pool

import asyncio
import functools

from functools import partial

from common import util

# def init():
#     globals()["loop"] = asyncio.get_event_loop()

@util.threaded
def start_thread_loop():
    util.log("启动协程后台")
    # asyncio.set_event_loop(globals()["loop"])
    # globals()["loop"].run_forever()

    globals()["__pool__"] = Pool(32)
    # globals()["loop"] = core.loop()
    # globals()["loop"].run()

# async def ____(function, *args, **kwargs):
#     # 只适合执行一些短暂的任务，里面的循环会阻塞线程
#     await function(*args, **kwargs)


# 异步框架，无法获取返回值
# 只适合执行一些短暂的任务，里面的循环会阻塞线程
# 没有返回值
def _asyn(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        util.log(f"创建协程 {function} {function.__doc__}")
        globals()["__pool__"].spawn(partial(function, *args, **kwargs))
    return wrapper

def _await(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        gevent.sleep(0)
        return function(*args, **kwargs)
    return wrapper

def parallel_run(funcs):
    ret = gevent.joinall([
        gevent.spawn(_) for _ in funcs
    ])
    return [_.value for _ in ret]

# init()