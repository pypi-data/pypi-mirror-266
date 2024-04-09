#!/bin/env python3

import os
import ssl
import time
import json
import functools
import datetime
# import urllib.request
# import urllib.parse

import contextlib
import threading
# import logging, traceback
from pdb import set_trace as strace
from traceback  import format_exc as dumpstack

# from common import util
from e4ting import log
from .util import now,today
import redis

class MapValueRedis(object):
    pool = None
    """docstring for MapInfoRedis"""
    def __init__(self, *kargs, **kwargs):
        self.db      = 2
        self.rc      = None
        self.level   = "info"
        self.timeout = 30
        self.host    = "redis.com"
        self.port    = 6379
        self.period  = 0
        self.password= None # "P@ssw0rd.C0m"
        [ setattr(self, k, v) for k,v in kwargs.items() ]
        self.load()

    def format_v(self, v):
        if v == None:
            return ""
        if type(v) == bool:
            return int(v)
        if type(v) in [ dict, list]:
            return json.dumps(v, ensure_ascii=False)
        return v

    def getall(self):
        return { _:self[_] for _ in self.keys() }

    def keys(self, v="*", start=0, limit=0):

        if limit > 0:
            return self.scan(start, limit)
        return self.rc.keys(v)

    def goto_iter(self, flag=0):

        ret = self.rc.scan(flag, '*', 100)
        self.__iter_flag__ = ret[0]
        self.__iter_data__ = iter(ret[1])

    def __iter__(self):
        # strace()
        self.goto_iter(0)
        return self

    def __next__(self):

        if int(self.__iter_flag__) == 0:
            return next(self.__iter_data__)

        try:
            return next(self.__iter_data__)
        except StopIteration:
            # log.info("断开了")
            self.goto_iter(self.__iter_flag__)

        return next(self.__iter_data__)

    def scan(self, start=0, limit=1):
        return self.rc.scan(start, '*', limit)[1]

    def __getitem__(self, key):
        return self.rc.get(key)

    def __setitem__(self, key, value):
        if not key:
            return None

        log.info("修改 {} {}".format(key, value))
        self.rc.set(key, value)

    def __add__(self, key):
        # 自增变量
        log.info("自增 {}".format(key))
        self.rc.incr(key)
        return self

    def iadd(self, key, v=1):
        return self.rc.incr(key, int(v))

    def add(self, key, v=1):
        return self.rc.incr(key, int(v))

    def __delitem__(self, key):
        if not key:
            return None
        log.info("删除 {}".format(key))
        # with util.lock_run(self.lock):
            # del self.data[key]
            # self.dump()
        self.rc.delete(key)

    def __contains__(self, key):
        return self.rc.exists(key)

    def __len__(self):
        return self.rc.dbsize()

    def expire(self, key, ex=60):
        return self.rc.expire(key, ex)

    def clearall(self):
        log.info("清空 {}".format(str(self)))
        return self.rc.flushdb()

    def none_log(self):
        self.level = "debug"

    def load(self):
        # if '__redis_conn__' not in globals():
        #     globals()["__redis_conn__"] = redis.StrictRedis(host='redis.com', port= 6379, db= self.db)
        # log.info("连接 {}".format(str(self)))
        if not MapValueRedis.pool:
            if self.password:
                MapValueRedis.pool = redis.ConnectionPool(host=self.host, port= self.port, db= self.db, decode_responses=True, password=self.password)
            else:
                MapValueRedis.pool = redis.ConnectionPool(host=self.host, port= self.port, db= self.db, decode_responses=True)

        if self.rc != None: # 不重复建立连接
            return
        self.rc = redis.StrictRedis(connection_pool=MapValueRedis.pool)

    def __repr__(self):
        return "redis://{self.host}:{self.port}/{self.db}".format(self=self)

class RedisCommon(MapValueRedis):

    def string(self, key):
        return self.rc.get(key)

    def set(self, key):
        return self.rc.smembers(key)

    def list(self, key):
        return self.rc.lrange(key, 0, -1)

    def hash(self, key):
        return self.rc.hgetall(key)

    def zset(self, key):
        return self.rc.zrange(key, 0, -1)

    def __getitem__(self, key):
        _funcs = {
            "string" : self.string
        }
        return getattr(self, self.rc.type(key))(key)

class MapDictRedis(MapValueRedis):

    def add(self, key, field, v=1):
        log.debug("{} 自增 {} {} {}".format(str(self), key, field, v))
        return self.rc.hincrby(key, field, v)

    def getkey(self, key, name):
        return self.rc.hget(key, name)

    def delitem(self, key, item):
        if not item:
            return True
        if type(item) is list:
            return self.rc.hdel(key, *item)
        else:
            return self.rc.hdel(key, item)

    def __getitem__(self, key):
        data = self.rc.hgetall(key)
        # data = { k.decode():v.decode() for k,v in data.items()}
        return data

    def __setitem__(self, key, value):
        if not key:
            return None
        # with util.lock_run(self.lock):
        value = { k:self.format_v(v) for k,v in value.items()}
            # if v == None:
            #     value[k] = ""
            # if type(v) == bool:
            #     value[k] = int(v)
            # if type(v) in [ dict, list]:
            #     value[k] = json.dumps(v, ensure_ascii=False)

        log.debug("修改 {} {}".format(key, value))
        self.rc.hmset(key, value)
        # self.rc.hset(key, mapping=value)

class MapSetRedis(MapValueRedis):

    # def decode(self, string):

    def __getitem__(self, key):
        data = self.rc.smembers(key)
        # data = { k.decode():v.decode() for k,v in data.items()}
        # data = { k.decode():v.decode() for k,v in data.items()}
        # data = [ k.decode() for k in data]
        return data

    def __setitem__(self, key, value):
        if not key:
            return None
        # with util.lock_run(self.lock):
        log.info("修改 {} {}".format(key, value))
        # 先清空
        del self[key]
        # 再赋值
        self + (key, value)

    def exists(self, key, item):
        return self.rc.sismember(key, item)

    def delitem(self, key, item):
        if not item:
            return True
        if type(item) is list:
            return self.rc.srem(key, *item)
        else:
            return self.rc.srem(key, item)

    def getlen(self, key):
        return self.rc.scard(key)

    def add(self, key, value):
        log.info("追加", str(self), key, value)
        self.rc.sadd(key, value)

    def append(self, key, value):
        log.info("追加", str(self), key, value)
        self.rc.sadd(key, value)

    def __add__(self, item):
        # key, value = item
        # self.rc.sadd(key, *value)
        self += item

    def __iadd__(self, item):
        key, value = item
        if value:
            log.info("追加", value)
            value = [ self.format_v(_) for _ in value]
            self.rc.sadd(key, *value)
        return self

    def __delitem__(self, key):
        # self.rc.spop(key)
        self.rc.delete(key)

class MapListRedis(MapValueRedis):

    def __getitem__(self, key):
        if hasattr(self, "key") and self.key :
            raise ValueError("""不允许 self["{}"]["{}"] 多层调用形式""".format(self.key, key))
        return MapListRedis(key=key, db=self.db, rc=self.rc, level=self.level, period=self.period)

    def exists(self, key, item):
        return self.rc.sismember(key, item)

    # def __add__(self, item):
    #     if value:
    #         self.rc.lpush(self.key, value)
    #     return self

    """ 减法重载 """
    # def __sub__(self, item):
    #     return self

    def __len__(self):
        assert hasattr(self, "key") and self.key

        return self.rc.llen(self.key)

    def __gt__(self, num):
        """ 重载 > 消费者，信息出栈，阻塞 """

        assert hasattr(self, "key") and self.key

        log.info("消费者(阻塞) {} {}个".format(self.key, num), level=self.level)
        if num == 1:
            ret = self.rc.brpop(self.key, self.timeout)
            if ret:
                return ret[1]
            else:
                return ret
        return [self.rc.brpop(self.key, self.timeout)[1] for i in range(num)]

    def __rshift__(self, num):
        """ 重载 >> 消费者，信息出栈，num代表出栈 个数 """

        assert hasattr(self, "key") and self.key

        log.info("消费者(非阻塞) {} {}个".format(self.key, num), level=self.level)

        if num == 1:
            ret = self.rc.rpop(self.key)
            # log(ret)
            if ret:
                return ret[1]
            else:
                return ret
        return [self.rc.rpop(self.key)[1] for i in range(num)]

    def __lt__(self, value):
        """ 重载 < 生产者，信息入栈，覆盖式入栈 """
        del self[self.key]
        return self << value

    def __lshift__(self, value):
        """ 重载 << 生产者，信息入栈，追加式入栈 """

        assert hasattr(self, "key") and self.key

        if value:
            log.info("{} 生产者 {} {}".format(str(self), self.key, value), level=self.level)
            self.rc.lpush(self.key, value)
            if self.period:
                self.expire(self.key, self.period)
        return True

    # def __iadd__(self, value):
    #     return self + value

    # def __delitem__(self, key):
    #     # self.rc.spop(key)
    #     self.rc.delete(key)

def key_(*params, **kwargs):
    return ":".join(list(params) + [ ":".join([k, v]) for k,v in kwargs.items()])

""" 系统配置 """
redis_conf    = MapValueRedis(db=0)
redis_0_black = MapSetRedis(db=0)
# redis_running = MapDictRedis(db=0)

""" botnet连接信息 """
redis_botnet_conns = MapDictRedis(db=1)
redis_botnet_clients = redis_botnet_conns

""" botnet实时登录会话 """
redis_botnet_sessions = MapDictRedis(db=2)

""" 消费者，生产者 """
redis_queues          = MapListRedis(db=6, level="debug")
redis_3_cmd_queues    = MapListRedis(db=6, timeout=1, level="debug")
redis_6_poker         = MapSetRedis(db=6, level="debug")

""" 小数据分析平台的配置 """
redis_little_conf = MapDictRedis(db=4)

""" 通知系统用来保存配置用 """
redis_4_cache = MapDictRedis(db=4)

""" 小数据分析平台的中间结果 """
redis_little_result = MapValueRedis(db=5)
redis_5_poker       = redis_little_result

CELERY_RESULT_BACKEND = 'redis://redis.com:6379/6'
CELERY_BROKER_URL     = 'redis://redis.com:6379/6'

""" toB 对账带宽 """
redis_reconciliation = MapDictRedis(db=7)

""" 聊天数据分析 """
redis_chats         = MapDictRedis(db=8)

""" 浏览器ID """
redis_browsers   = MapDictRedis(db=11)

""" 临时运行数据 """
redis_temp_running   = MapDictRedis(db=12, level="debug")
redis_temp_run_list  = MapSetRedis(db=12, level="debug")
redis_flask_session  = redis.Redis(host='redis.com', port='6379', db=15)
redis_auth_token     = MapDictRedis(db=15, level="debug")
# """ 在线设备列表，以SN为key"""
# redis_online_dev = MapValueRedis(db=13)

# """ 设备列表，以SN为key，用户搜索"""
# redis_dev = MapDictRedis(db=14)

@contextlib.contextmanager
def record_action_and_limit(key, timeout=60, **kwargs):

    flag_can_run = True
    start = time.time()
    redis_temp_running[key] = {
        "start" : start,
        **kwargs
    }

    if key not in redis_temp_running:
        lasttime = 0
    else:
        lasttime = redis_temp_running[key].get("time", 0)
    flag_can_run = float(lasttime) + timeout < time.time()

    yield flag_can_run

    end = time.time()
    redis_temp_running.add(key, "count")
    redis_temp_running[key] = {
        "time": end,
        "usetime" : end - start,
    }

def pipe_batch_execute(function):
    @functools.wraps(function)
    def wrapper(redis=None, *args, **kwargs):
        # strace()
        assert redis
        with redis.rc.pipeline(transaction=False) as pipe:
            function(redis=redis.__class__(rc=pipe), *args, **kwargs)
            ret = pipe.execute()
        return ret
    return wrapper

def create_random():
    key = key_("api", "random")
    v = redis_conf.add(key)
    return v

def salt():
    # md5加盐
    return redis_conf["salt"]

def default_status():
    return redis_conf["default_status"]

def default_role():
    return redis_conf["default_role"]

def create_token_id():
    """ 创建密码验证id """
    key = key_("api", "auth", "id")
    v = redis_conf.add(key)
    return v

def create_poker_id(flag="record"):
    """ 创建poker模块所需id """
    key = key_("api", "poker", flag, "id")
    v = redis_conf.add(key)
    return v

def alloc_task_id():
    key = key_("api", "task", "id")
    v = redis_conf.add(key)
    return v

def alloc_ws_id():
    key = key_("api", "ws", "id")
    v = redis_conf.add(key)
    return v

def get_task_key(_id):
    return key_("api", "task", "result", str(_id))

def send_task(key, cmd):

    cmd_id = alloc_task_id()
    data = dict(cmd, tid=cmd_id)

    redis_queues[key] << json.dumps(data)
    return get_task_key(cmd_id)

def save_task_result(data):
    assert "tid" in data

    cmd_id = data["tid"]
    key = get_task_key(cmd_id)

    redis_queues[key] << json.dumps(data)

    # 超过一小时不取结果，就销毁
    redis_queues.expire(key, 3600)

def read_task_result(key):
    ret = redis_queues[key] > 1
    if not ret:
        return None
    ret = json.loads(ret)
    return ret["data"]

def save_token(data, timeout):
    key = key_("api", "auth", str(data["_id"]))
    redis_auth_token[key] = data
    redis_auth_token.expire(key, timeout)

def info_2_id(info):
    uid  = create_random()
    flag = util.baseconvert(util.crc(str(uid)), 10, 62)
    redis_4_cache[flag] = {
        "flag" : flag,
        "_id"  : uid,
        "info" : info
    }
    return flag

def id_2_info(flag):
    if not flag in redis_4_cache:
        return None
    redis_4_cache.add(flag, "view")
    data = redis_4_cache[flag]
    return data.get("info", None)

# def publish(key, data=""):
#     product = redis_conf.rc.pubsub()
#     product.subscribe(key)
#     redis_conf.rc.publish(key, redis_conf.format_v(data))
#     return True

# def listen(key):
#     product = redis_conf.rc.pubsub()
#     type,channel,data = product.parse_response()
#     return data

class WechatMsgAPI():
    def __init__(self):
        self.key = "api:wechat:msg"
        self.init()

    def init(self):
        self.product = redis_conf.rc.pubsub()
        self.product.subscribe(self.key)

    def init_listen(self):
        # ret = listen(self.key)
        type,channel,data = self.product.parse_response()
        log(f"{self.key} 监听成功", type, channel, data)

    def decode(self, data:str):
        try:
            data = json.loads(data)
        except:
            pass
        return data

    def publish(self, data:dict):
        redis_conf.rc.publish(self.key, redis_conf.format_v(data))
        return True

    def listen(self):
        type,channel,data = self.product.parse_response()
        return self.decode(data)

class WSTaskAPI():
    # websocket长连接操作接口

    def __init__(self, uid):
        self.uid  = uid
        self.thead = "api:task:queue"
        self.rhead = "api:task:result"
        self.signal_online  = key_("api", "ws", "signal", "online")
        self.signal_offline = key_("api", "ws", "signal", "offline")

    def init(self):
        # self.new()
        self.online = redis_conf.rc.pubsub()
        self.online.subscribe(self.signal_online)
        self.offline = redis_conf.rc.pubsub()
        self.offline.subscribe(self.signal_offline)

    def alloc_id(self, name="ws"):
        key = key_("api", name, "id")
        return redis_conf.add(key)

    def get_task_key(self, tid):
        return key_(self.rhead, str(self.uid), str(tid))

    def new(self):
        # self.tid = alloc_task_id()
        return alloc_task_id()

    def notify(self, _type="online"):
        assert _type in ["online", "offline"]
        if _type == "online":
            num = redis_conf.rc.publish(self.signal_online, str(self.uid))
        elif _type == "offline":
            num = redis_conf.rc.publish(self.signal_offline, str(self.uid))
        return num

    def listen_online(self):
        ret = self.online.parse_response()
        # log(ret)
        type,channel,data = ret
        if type == "subscribe":
            log(f"频道 {channel} 订阅成功 {data}")
            return self.listen_online()

        if type == "message":
            return int(data)

    def listen_offline(self):
        ret = self.offline.parse_response()
        # log(ret)
        type,channel,data = ret
        if type == "subscribe":
            log(f"频道 {channel} 订阅成功 {data}")
            return self.listen_offline()

        if type == "message":
            return int(data)

    def encode(self, data:dict):
        return json.dumps(data)

    def decode(self, data:str):
        return json.loads(data)

    def tpush(self, data:dict):
        # 发送任务
        tid = self.new()
        key = self.thead
        payload = dict(uid=self.uid, tid=tid, data=data)
        log(payload)
        redis_queues[key] << self.encode(payload)
        return self.get_task_key(tid)

    def tpull(self):
        # 接收任务 ， 这个接口比较特殊，它不需要uid
        key = self.thead
        task = redis_3_cmd_queues[key] > 1
        if not task:
            return False,None
        task = self.decode(task)
        uid = task["uid"]
        del task["uid"]
        return uid, task

    def rpush(self, data:dict):
        # 写入任务结果
        # self.uid
        # data = self.decode(data)
        if not type(data) is dict:
            log(f"返回数据格式不合法{data}")
            return False
        if not "tid" in data:
            log(f"返回数据格式不合法{data}")
            return False
        tid = data["tid"]
        key = self.get_task_key(tid)
        # log(data)
        redis_queues[key] << self.encode(data)
        redis_queues.expire(key, 3600)
        return True

    def rpull(self, key):
        # 获取任务结果，应该从结果中剥离tid这些信息
        # self.tid
        # self.uid
        # key = _id or self.get_task_key()
        ret = redis_queues[key] > 1
        if not ret:
            return False
        ret = self.decode(ret)
        if "data" not in ret:
            return None
        return ret["data"]

class PokerAPI(WSTaskAPI):
    """ game操作API """
    def __init__(self, rid):
        self.uid  = rid
        self.thead = "poker:task:queue"
        self.rhead = "poker:task:result"
        self._room = key_("poker", "room", "{uid}", "data")
        self.key = self._room.format(uid=self.uid)
        self.room_key = "poker:room:signal"

    def init_room_env(self):

        self._room_singal = redis_conf.rc.pubsub()
        self._room_singal.subscribe(self.room_key)

        ret = self._room_singal.parse_response()
        type,channel,data = ret
        if type == "subscribe":
            log(f"频道 {channel} 订阅成功 {data}")

    def room_push(self, uid, **data):
        num = redis_conf.rc.publish(self.room_key, json.dumps(dict(data, uid=uid), ensure_ascii=False))
        return num

    def room_pull(self):
        ret = self._room_singal.parse_response()
        _type,channel,data = ret
        if _type != "message":
            return self.room_pull()
        return json.loads(data)

    def register(self):
        self._room_data = redis_conf.rc.pubsub()
        self._room_data.subscribe(self.key)

    def tpush(self, data):
        num = redis_conf.rc.publish(self.key, json.dumps(data, ensure_ascii=False))
        return num

    def tpull(self):
        ret = self._room_data.parse_response()
        type,channel,data = ret
        if type == "subscribe":
            log(f"频道 {channel} 订阅成功 {data}")
            return self.listen_online()

        if type == "message":
            return json.loads(data)

    def __lshift__(self, data):
        """ [ self << task ] 往self扔东西 """
        return self.tpush(data)

    def __rshift__(self, func=print):
        """ [ self >> task ] 往self 外拉东西 """
        return func(self.tpull())

    def __lt__(self, data):
        """ [ self < task ] 往self扔东西 """
        return self.rpush(data)

    def __gt__(self, func=print):
        """ [ self > task ] 往self 外拉东西 """
        return func(self.rpull())

    # def __le__(self, data):
    #     """ [ self <= task ] 往self扔东西 扔任务"""
    #     return self.tpush(data)

    # def __ge__(self, num=1):
    #     """ [ self => task ] 往self 外拉东西 拉任务"""
    #     return self.tpull()

    # def __ilshift__(self, data):
    #     """ [ self << task ] 往self扔东西 扔结果"""
    #     return self.rpush(data)

    # def __irshift__(self, key=""):
    #     """ [ self >> task ] 往self 外拉东西 拉结果"""
    #     return self.rpull()

class INRC():
    def __init__(self, key):
        self.key = key

    def __get__(self, instance, owner):
        # log(self.key, instance, owner)
        return redis_conf.add(self.key)

class NewID():

    ws = INRC("api:ws:id")
    task = INRC("api:task:id")

    wechat = INRC("api:wechat:id")

    poker = INRC("api:poker:id")
    round = INRC("api:poker:round:id")
    room = INRC("api:poker:room:id")
    player = INRC("api:poker:player:id")
    maker = INRC("api:poker:maker:id")
    record = INRC("api:poker:record:id")
    fundpool = INRC("api:poker:fundpool:id")
    # record = INRC("api:poker:record:id")


class RunningInfo(object):
    # 运行状态信息
    attr = {"__uid__", "__key__"}
    def __init__(self, uid=0, mod="", role=""):
        self.__uid__ = uid
        self.__key__ = key_(mod, role, "running", str(uid))
        # self.__setattr__ = self.setattr

    def refresh(self):
        self._time_ = time.time()
        self._date_ = now()

    def write(self, **kwargs):
        redis_temp_running[self.__key__] = kwargs
        # self.refresh() # Add By cdj 2021-09-28 08:48:13 绝对不可以调
        return True

    def read(self, k=None):
        if not k:
            # 默认读取所有配置
            return redis_temp_running[self.__key__]

        return redis_temp_running.getkey(self.__key__, k)

    def exists(self):
        # 配置项是否存在
        return self.__key__ in redis_temp_running

    def __setattr__(self, k, v):
        # 极其危险
        # strace()
        if k in RunningInfo.attr:
            super().__getattribute__("__dict__")[k] = v
            return

        return self.write(**{k:v})

    def __getattr__(self, k):
        return self.read(k)

    def __repr__(self):
        return f"{self.__uid__}"

    def timeout(self, howlong=3600):
        redis_temp_running.expire(self.__key__, howlong)

if __name__ == '__main__':
    ret = info_2_id("http://xx.xxx.cn/test/fuck")
    log(ret)

    for i in range(10):
        info = id_2_info(ret)
        log(info)

    # for k in redis_conf:
    #     log(k)
    # strace()
    # redis_queues["test"] << time.time()
    # redis_queues["test"] << time.time()
    # redis_queues["test"] << time.time()
    # ret = redis_queues["test"] > 1
    # log(ret)

    # ret = redis_queues["test"] >> 1
    # log(ret)

    # # 盐值
    # redis_conf["salt"] = "bf4fd65f83b1e1a0189b269355539e18"
    # redis_conf["ws_timeout"] = 120
    # redis_conf["session_timeout"] = 60*60*24*30
    # redis_conf["default_role"] = "common"
    # redis_conf["default_status"] = "active"
    # redis_conf["valid_user_name"] = "".join([ str(_) for _ in range(0, 10)] + [ chr(_) for _ in range(ord("a"), ord("z") + 1)] + [ chr(_) for _ in range(ord("A"), ord("Z") + 1)]) + "_-"

