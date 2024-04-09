#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    [模块名]
    Add By :antiy chendejun@antiy.cn 2022-10-15 18:18:31
"""
import sys,os
import functools
import time,json
from pdb import set_trace as strace
from traceback  import format_exc as dumpstack

from common import util
from common.utilredis import NewID,MapDictRedis

redis_temp_running = MapDictRedis(db=0)

class INRC():
    def __init__(self, key="cache:api:total", attr="attr"):
        self.key = key
        self.attr = attr

    def __call__(self):
        return redis_temp_running.add(self.key, self.attr)

    def __get__(self, instance, owner):
        return redis_temp_running.add(self.key, self.attr)

class StringID(INRC):
    def __get__(self, instance, owner):
        return str(redis_temp_running.add(self.key, self.attr))

class RedisCache(object):
    # 运行状态信息
    attr = {"__uid__", "__key__"}
    key  = INRC(attr="common")
    def __init__(self, mod="", uid=0):
        self.__uid__ = uid
        self.__key__ = f"cache:{mod}:{str(uid)}"

    def refresh(self):
        self._time_ = time.time()
        self._date_ = now()

    def set(self, **kwargs):
        redis_temp_running[self.__key__] = kwargs
        # self.refresh() # Add By cdj 2021-09-28 08:48:13 绝对不可以调
        return True

    def get(self, k=None):
        if not k:
            # 默认读取所有配置
            return redis_temp_running[self.__key__]

        return redis_temp_running.getkey(self.__key__, k)

    def pushd(self, data):
        if not data is str:
            data = json.dumps(data, ensure_ascii=False)
        redis_temp_running.rc.lpush(self.__key__, data)

    def popd(self, timeout=0.1):
        data = redis_temp_running.rc.brpop(self.__key__, timeout) or "{}"
        if data:
            data = data[1]
        return json.loads(data)

    def keys(self):
        # key = self.__key__.replace(self.__uid__, "*")
        keys = redis_temp_running.keys(self.__key__)
        pos = len(self.__key__) - 1
        return [ _[pos:] for _ in keys ]

    def exists(self):
        # 配置项是否存在
        return self.__key__ in redis_temp_running

    def __setattr__(self, k, v):
        # 极其危险
        # strace()
        if k in RedisCache.attr:
            super().__getattribute__("__dict__")[k] = v
            return

        return self.set(**{k:v})

    def __getattr__(self, k):
        return self.get(k)

    def __repr__(self):
        return f"{self.__uid__}"

    def timeout(self, howlong=31536000):
        # 默认超时一年
        redis_temp_running.expire(self.__key__, howlong)

    def __del__(self):
        self.timeout()

class TemplateCache(RedisCache):
    key  = StringID(attr="template")
    def __init__(self, id):
        super().__init__("template", id)

    def __del__(self):
        # 保留1个月
        self.timeout(3600*24*365)

class ConnCache(RedisCache):
    def __init__(self, sn):
        super().__init__("conn", sn)

    def __del__(self):
        # 在内存中保留 5 min
        self.timeout(300)

class MacCache(RedisCache):
    def __init__(self, sn):
        super().__init__("mac", sn)

    def __del__(self):
        # 在内存中保留 5 min
        self.timeout()

class DeviceCache(RedisCache):
    def __init__(self, sn):
        super().__init__("device", sn)

    def __del__(self):
        # 在内存中保留一个星期
        self.timeout(604800)

class ReportCache(RedisCache):
    def __init__(self, sn):
        super().__init__("report", sn)

    def __del__(self):
        # 在内存中保留一个星期
        self.timeout(604800)

class IPCache(RedisCache):
    def __init__(self, ip):
        super().__init__("ip", ip)

class TokenCache(RedisCache):
    def __init__(self, token):
        super().__init__("token", token)

    def __del__(self):
        self.timeout(7200)

class FRPCache(RedisCache):
    def __init__(self, frp):
        super().__init__("frp", frp)

    def __del__(self):
        # 保留5min钟
        self.timeout(300)

class UserCache(RedisCache):
    def __init__(self, phone):
        super().__init__("user", phone)

    def __del__(self):
        # 保留1个月
        self.timeout(2592000)

class RoleCache(RedisCache):
    def __init__(self, id):
        super().__init__("role", id)

    def __del__(self):
        # 保留1个月
        self.timeout(2592000)

class CodeCache(RedisCache):
    def __init__(self, phone):
        super().__init__("code", phone)

    def __del__(self):
        # 有效期为60s
        self.timeout(300)

class IncomeCache(RedisCache):
    def __init__(self, date):
        super().__init__("income", date)

    def __del__(self):
        # 有效期为90天
        self.timeout(7776000)

class UserIncomeCache(RedisCache):
    def __init__(self, date):
        super().__init__("user_income", date)

    def __del__(self):
        # 有效期为365天
        self.timeout(31536000)

class SLAConfig(RedisCache):
    def __init__(self):
        self.__uid__ = "sla"
        self.__key__ = f"api:config:sla"

class WithdrawConfig(RedisCache):
    def __init__(self):
        self.__uid__ = "withdraw"
        self.__key__ = f"api:config:withdraw"

    def get_days(self):
        return json.loads(self.month)

class RemoteCache(RedisCache):
    def __init__(self, sn):
        super().__init__("remote", sn)

    # def get_cmd(self):
        # 推送拨号信息
        # pppoes = get_pppoes(sn)
        # remote = RemoteCache(sn)
        # remote.pushd(dict(action="serverDial", payload=[self.format_ppoe(_) for _ in pppoes]))
        # self.popd()

    def __del__(self):
        # 只有5min有效期
        self.timeout(300)

class APICache(RedisCache):
    def __init__(self, name="map"):
        super().__init__("url", name)

class SyslogCache(RedisCache):
    def __init__(self, ip="127.0.0.1", key="map"):
        super().__init__("syslog", "{ip}:{key}".format(ip=ip, key=key))

    def __del__(self):
        # 只有5min有效期
        self.timeout(300)

def redis_cache_frp(function):
    @functools.wraps(function)
    def wrapper(uid, *args, **kwargs):
        payload = function(uid,*args, **kwargs)
        if not payload:
            return {}

        cache = FRPCache(uid)
        diff = {cache.get(k) == payload.get(k, "") for k in ["status", "last_start_time", "last_close_time"]}
        if not False in diff:
            # 数据没有发生变化
            return {}
        # old = cache.get()
        # payload = { k:v for k,v in data.items() if old.get(k, None) != v }
        if payload:
            cache.set(**payload)

            # dev = DeviceCache(uid)
            # dev.status = cache.status
            # cache.timeout(86400)
        return payload
    return wrapper

