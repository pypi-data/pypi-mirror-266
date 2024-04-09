#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    基础任务 模块
    Add By :
        test
        test@gmail.com
        2021-09-20 16:21:40
"""
import sys,os
import time,json
from pdb import set_trace as strace
from traceback  import format_exc as dumpstack
from functools  import partial

from .util import log
from .utilredis import alloc_task_id,redis_3_cmd_queues,redis_queues,key_

class TaskBase():
    def __init__(self, uid):
        self.uid  = uid
        self.thead = "api:task:queue"
        self.rhead = "api:task:result"
        self.init()

    def init(self):
        self.new_id()

    # @staticmethod
    def new_id(self):
        # Add By cdj 2021-09-20 16:32:22 创建id
        self._id = alloc_task_id()
        return self._id

    def get_task_key(self, tid):
        return key_(self.rhead, str(self.uid), str(tid))

    def pack(self, mod, *args, **kwargs):
        payload = {}
        payload = dict(payload, mod=mod, tid=self._id, uid=self.uid)
        payload = dict(payload, args=list(args))
        if kwargs:
            payload = dict(payload, kwargs=dict(kwargs))
        return self.encode(payload)

    def decode(self, data):
        return json.loads(data)

    def encode(self, data):
        return json.dumps(data, ensure_ascii=False)

    def read(self):
        """ 接收执行任务 完成 上半部 """
        key = self.thead
        data = redis_queues[key] > 1
        if not data: return None
        return self.decode(data)

    def write(self, data:dict):
        """ 写入任务结果 完成 下半部 """
        if not type(data) is dict:
            util.log(f"返回数据格式不合法{data}")
            return False
        if not "tid" in data:
            util.log(f"返回数据格式不合法{data}")
            return False
        tid = data["tid"]
        key = self.get_task_key(tid)
        # util.log(data)
        redis_queues[key] << self.encode(data)
        redis_queues.expire(key, 3600)
        return True

    def push(self, data):
        """ 执行任务 上半部 """
        key = self.thead
        redis_queues[key] << data
        return self.get_task_key(self._id)

    def pull(self, key):
        """ 执行任务 下半部 """
        ret = redis_queues[key] > 1
        if not ret:
            return False
        ret = self.decode(ret)
        if "data" not in ret:
            return None
        return ret["data"]

    def notify(self, msg):
        self.init()
        data = self.pack("notify", msg)
        self.push(data)
        return True

    def exec(self, mod, *args, **kwargs):
        """
            {
                "mod" : "hello",
                "args" : ["test"],
                // "kwargs" : {"name": "test1"},
            }
        """
        self.init()
        data = self.pack(mod, *args, **kwargs)
        # log(data)
        key = self.push(data)
        ret = self.pull(key)
        return ret

    def __getattr__(self, fname):
        return partial(self.exec, fname)


