#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    基础请求处理模块
"""

import os,sys
import json
import collections
import functools
from   pdb import set_trace as strace
from   traceback  import format_exc as dumpstack
import threading
import contextlib
import datetime,time
import traceback
from   flask       import redirect,request,make_response,session

from   utilredis   import ( redis_conf,
                            redis_0_black,
                            key_,
                            redis_temp_running,
                            redis_temp_run_list
                          )
from   mongo       import ( db_res,
                            db_roles,
                            db_users,
                            db_menus,
                            db_folders,
                            db_IPs
                          )
import util
from util import ip_local

class BaseReq(object):
    """ 基础请求处理模板 """
    def __init__(self, *kargs, **kwargs):
        self.nginx_path = "/.sysroot/home/nginx/html/"
        self.icp_path   = "{}/icp".format(self.nginx_path)
        self.IamGod     = False # 关闭上帝模式

    def ip_local(self, ip):
        return ip_local(ip)

    # @property
    # def IamGod(self):
    #     return self._IamGod

    # @IamGod.setter
    # def IamGod(self, v):
    #     if v:
    #         util.log("开启上帝模式")
    #     else:
    #         util.log("关闭上帝模式")
    #     self._IamGod = v

    @property
    def bindid(self):
        return session.get('BINDID')

    @bindid.setter
    def bindid(self, bid):
        session["BINDID"] = bid
        # session.permanent = True

    def __getitem__(self, key):
        """
            获取cookie中的属性
        """
        if hasattr(self, key):
            return getattr(self, key)
        return session.get(key)

    def __setitem__(self, key, value):
        """
            设置 cookie 属性
        """
        setattr(self, key, value)
        session[key] = value

    @property
    def user(self):
        # util.log(request.cookies.get("UUID"))
        return session.get('UUID')

    @user.setter
    def user(self, uid):
        session["UUID"] = uid
        session.permanent = True
        # app.permanent_session_lifetime = timedelta(minutes=10)
        # resp = make_response("success")
        # resp.set_cookie("UUID", uid, max_age=3600)
        # util.log(dict(resp.headers)["Set-Cookie"])
        # strace()
        # request.cookies["UUID"] = uid

    @property
    def default_role(self):
        return redis_conf["default_role"]

    @property
    def super_role(self):
        return "admin"

    def check_editable(self, res):
        util.log(self.role, res)
        if self.role == res["role"] or self.role == self.super_role:
            return True
        return False

    @property
    def data(self):
        return request.json

    @property
    def res_name(self):
        # 当前访问的资源的名字
        return get_req_resuorce()

    @property
    def role(self):
        if not self.user :
            return "guest"
        return db_users[self.user].get("role", "common")

    def fill_item(self, data={}):
        data["time"] = util.now()
        data["_"] = time.time()
        return data

    def filter(self, data):
        # util.log(request.args)
        condition = dict(request.args)
        # del condition["_"]
        condition = [ (k,v.strip()) for k,v in condition.items() if v.strip() and k != '_']
        condition = [ "('{k}' not in item or '{v}' in item['{k}'])".format(k=k, v=v) for k,v in condition]
        condition = " and " .join(condition)
        # util.log(condition)
        if not condition:
            return data
        def __(item):
            util.log(item)
            return eval(condition)
        return [_ for _ in data if __(_)]

    @property
    def pageCurrent(self):
        return int(request.args.get("pageCurrent", 0))

    @property
    def pageSize(self):
        return int(request.args.get("pageSize", 100))

    @property
    def size(self):
        return int(request.args.get("size", 100))

    @property
    def start(self):
        return (self.page - 1) * self.size

    @property
    def end(self):
        return self.start + self.size

    @property
    def order(self):
        return request.args.get("order", "")

    @property
    def desc(self):
        return request.args.get("desc", None)

    @property
    def page(self):
        return int(request.args.get("page", 1))

    @property
    def current(self):
        return int(request.args.get("current", 1))

    @property
    def offset(self):
        return max(self.page - 1, 0) * self.size

    @property
    def status(self):
        return redis_conf["default_status"]

    def check_user_status(self, user):
        return db_users[user]["status"] == "active"

    @property
    def valid_char(self):
        return redis_conf["valid_user_name"]

    @property
    def salt(self):
        # md5加盐
        return redis_conf["salt"]

    @property
    def passwd(self):
        return db_users[self.user]["password"]
        # p_crc  = self.md5(passwd + self.salt)
        # if p_crc != db_users[user]["password"]

    @passwd.setter
    def passwd(self, passwd):
        db_users[self.user] = {"password" : self.passwd_encode(passwd)}

    def passwd_encode(self, passwd):
        return self.md5(passwd + self.salt)

    def check_passwd(self, passwd, user=None):
        if user:
            return self.passwd_encode(passwd) == db_users[user]["password"]
        return self.passwd_encode(passwd) == self.passwd

    @contextlib.contextmanager
    def check_and_set_code(self, code):

        key = key_("api", "acl", "login", "luosimao", code)
        ret = key in redis_temp_running
        # if ret:
        #     ret = redis_temp_running[key].get(self.bindid, False)
        # 判断是否已验证过
        yield ret

        # 用一个字典来保存，以防接口被爆破， 暂时不做防护处理
        if not self.bindid:
            return
        redis_temp_running.add(key, self.bindid)
        if not ret:
            redis_temp_running.expire(key, 10 * 60)

    def check_robot_code(self, code):

        if "e4ting.cn" in self.refer:
            api_key = "bf4db134f59c40436440163a013b643a"
        elif "e4ting.top" in self.refer:
            api_key = "c32a81c2b6437cd52074a4f9e18c1a55"
        else:
            util.log("不支持此站点 {} 做验证码校验".format(self.refer))
            return False

        with self.check_and_set_code(code) as result:
            if not result:
                url = "https://captcha.luosimao.com/api/site_verify"
                data = {
                    # c32a81c2b6437cd52074a4f9e18c1a55
                    "api_key": api_key,
                    "response" : code,
                }
                ret = util.HTTP().post(url, data=data, headers={"Content-Type":"application/x-www-form-urlencoded"})
                util.log(ret)
                if ret["error"] != 0:
                    # 验证失败，直接return  不记录redis
                    ret = False
            ret = True
        return ret

    @property
    def refer(self):
        _refer = request.headers.get("Referer", "")
        # return request.referrer
        # util.log(Referer)
        return _refer

    @property
    def ip(self):
        ip   = request.headers.get("X-Real-Ip", request.remote_addr)
        # util.log(ip)
        return ip

    # def ip_local(ip):
    #     if ip in db_IPs:
    #         return db_IPs[ip]
    #     ret = util.get_ip_local(ip)
    #     if ret:
    #         db_IPs[ip] = ret
    #         return ret
    #     return None

    def md5(self, passwd):
        import hashlib

        m = hashlib.md5()
        m.update(str(passwd).encode(encoding='utf-8'))
        return m.hexdigest()

    def execute(self, uid, mod="", args=None, back=False, **kwargs):
        # mod="info", args=None,
        # if back:
        #     # 代表不要求client响应此请求
        #     url = "http://www.e4ting.cn/api/v1/socket/execute/{sn}?r=1".format(sn=uid)
        # else:
        #     url = "http://www.e4ting.cn/api/v1/socket/execute/{sn}".format(sn=uid)
        # # if args:
        # kwargs.update({"args" : args})
        # data = kwargs
        # ret = util.HTTP().post(url , data)
        # if ret["code"] != 200:
        #     util.log(uid, ret["data"])
        #     return False
        from botnet.device import Device
        return Device(uid=uid).exec(mod=mod, args=None)
        # return ret["data"]

    def e401(self, *kargs, **kwargs):
        """
            没登录 或者没有权限
        """
        return {
            "code" : 401,
            "msg"  : "没有权限",
            "res" : request.path,
            "location": "/login",
        }

    def e403(self, *kargs, **kwargs):
        """
            IP黑名单 或者 用户黑名单
        """
        return {
            "code" : 403,
            "msg"  : "禁止访问",
            "res" : request.path
        }

    def acl(self, attr):
        """ acl 控制器 """

        # util.log("attr={} {}".format(attr, self.name))
        # ret = "cannot" if attr == "get" else attr
        res = self.res_name

        ret = check_ip_black(self.ip)
        if ret:
            return super().__getattribute__("e403")

        ret = check_ip_res_black(self.ip, res)
        if ret:
            return super().__getattribute__("e403")

        # util.log(self.user)
        ret = check_permission(self.role, res)
        if not ret:
            return super().__getattribute__("e401")
        # util.log("正在访问 ", res, ret)
        counts = record_request(self.bindid, self.ip, self.name, self.user, self.role)
        return super().__getattribute__(attr)

    # def __getattribute__(self, attr):
    #     """ 拦截 get post put 等方法 """
    #     # util.log("self.{}".format(attr))

    #     if attr == '__dict__':
    #         # 防止 dict 被拦截 导致无限递归
    #         return super().__getattribute__(attr)

    #     # 上帝模式下，不做任何处理
    #     if "IamGod" in self.__dict__ and self.__dict__["IamGod"]:
    #         # strace()
    #         return super().__getattribute__(attr)

    #     if attr in ["get", "post", "put", "delete", "head", "connect", "patch", "trace"]:
    #         # return self.acl(attr)
    #         return super().__getattribute__("acl")(attr)
    #     return super().__getattribute__(attr)

def check_ip_black(ip):
    # IP是否在黑名单中
    key = key_("api", "acl", "black", "ip")
    return redis_0_black.exists(key, ip)

def check_ip_res_black(ip, res):
    # 该接口是否对特定IP拉黑
    key = key_("api", "acl", "black", "ip", res)
    return redis_0_black.exists(key, ip)

def check_permission(role, res):
    # 判断该角色对资源是否有权限
    # util.log(role, res)
    ret = db_roles[role].get(res, None)
    if ret :
        return True

    # 未登陆的用户，没有权限
    if role == "guest":
        return False

    ret = db_roles["guest"].get(res, None)
    if ret :
        return True

    return False

def get_req_resuorce():

    api_path = "/".join(request.path.split('/')[:4])
    ret = db_res.get(api=api_path)
    # util.log(api_path, ret, level="info")
    # 数据库中查不到这条资源
    if not ret:
        return None
    return ret[0]["name"]

def add_record(resource, **kwargs):
    # util.log(resource, kwargs)
    key = key_(api="acl", **kwargs)
    return redis_temp_running.add(key, resource),redis_temp_running.add(key, "__count__")

def record_request(bid, ip, resource, user=None, role=None):

    count1 = 0,0
    if bid:
        count1 = add_record(resource, bid=bid)
    count2 = add_record(resource, ip=ip)
    count3 = 0,0
    count4 = 0,0
    if user:
        count3 = add_record(resource, user=user)
    if role:
        count4 = add_record(resource, role=role)
    count5 = add_record(resource, res="count")
    return count1,count2,count3,count4,count5

if __name__ == '__main__':

    db_roles["common"] = {
            "desc" : "普通角色",
            "menus" : ["proxy"]
    }

