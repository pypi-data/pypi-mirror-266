#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    game 表名
    Add By :
        test
        test@gmail.com
        2021-09-20 15:41:48
"""
import sys,os
from pdb import set_trace as strace
from traceback  import format_exc as dumpstack

from e4ting.db import mongodb
from .utilredis import RunningInfo
from .util      import now


# 资金账户
db_poker_funds      = mongodb(host='mongo.com', db="poker",   table="funds", level="debug")

# 往来资金记录，转账&入账记录
db_poker_fund_record= mongodb(host='mongo.com', db="poker",   table="fund_record", level="debug")

# 下注记录
db_poker_allin      = mongodb(host='mongo.com', db="poker",   table="allins", level="debug")

# 房间
db_poker_rooms      = mongodb(host='mongo.com', db="poker",   table="rooms")

# 回合
db_poker_rounds     = mongodb(host='mongo.com', db="poker",   table="rounds")

# 庄家
db_poker_makers     = mongodb(host='mongo.com', db="poker",   table="makers", level="debug")

# 回合
db_poker_games      = mongodb(host='mongo.com', db="poker",   table="games")

# 保存每一副牌
db_poker_cards      = mongodb(host='mongo.com', db="poker",   table="cards", level="debug")

class DBBase():

    def __init__(self, _id=None, table=None):
        if _id:self._id = _id
        if table:self.table = table

    def __setattr__(self, key, value):
        self.table[self._id] = dict(key=value)

    def __getattr__(self, key):
        if not self._id in self.table:
            return None
        return self.table[self._id].get(key, None)

class DBFunds(DBBase):
    def __init__(self, _id):
        self._id = _id
        self.table = db_poker_funds

class DBRooms(DBBase):
    def __init__(self, _id):
        self._id = _id
        self.table = db_poker_rooms

class TexasRoomInfo(RunningInfo):
    def __init__(self, _id):
        super(TexasRoomInfo, self).__init__(mod="poker", role="room", uid=_id)
        self.init()

    def init(self):
        if self.exists():
            self.refresh()
            return
        # 从数据库中读出来
        log.info("即将从数据库加载", self.__uid__)
        data = db_poker_rooms[self.__uid__] or {}
        for k,v in data.items():
            # 跳过
            setattr(self, k, v)
        if data: self.refresh()

class TexasRoundInfo(RunningInfo):
    def __init__(self, _id):
        super(TexasRoundInfo, self).__init__(mod="poker", role="round", uid=_id)

    def init(self):
        if self.exists():
            self.refresh()
            return
        # 从数据库中读出来
        log.info("即将从数据库加载", self.__uid__)
        data = db_poker_rounds[self.__uid__] or {}
        for k,v in data.items():
            # 跳过
            setattr(self, k, v)

        if data: self.refresh()

    # def init_game(self):
    #     self.giveup = False
    #     self.allin  = False
    #     self.bet_amount = 0
    #     self.refresh()

class PlayerInfo(RunningInfo):
    def __init__(self, _id):
        super(PlayerInfo, self).__init__(mod="poker", role="player", uid=_id)

    def init(self):
        if self.exists():
            return
        # 从数据库中读出来
        log.info("即将从数据库加载", self)
        data = db_poker_funds[self.__uid__] or db_poker_makers[self.__uid__] or {}
        for k,v in data.items():
            # 跳过
            # if k in ["_id"]: continue
            setattr(self, k, v)
        self.refresh()

    def init_game(self):
        self.giveup = False
        self.allin  = False
        self.bet_amount = 0
        self.refresh()

    @property
    def online(self):
        return int(self.read("online") or "0")

    @property
    def sit(self):
        return int(self.read("sit") or "0")

    @property
    def allin(self):
        return int(self.read("allin") or "0")

    @property
    def bet(self):
        return int(self.read("bet") or "0")

    @property
    def giveup(self):
        return int(self.read("giveup") or "0")

    @property
    def score(self):
        return int(self.read("score") or "0")

    @property
    def room(self):
        return int(self.read("room") or "0")

    @property
    def round(self):
        return int(self.read("round") or "0")

    @property
    def amount(self):
        return int(self.read("amount") or "0")

    @property
    def cash(self):
        return self.amount   # int(self.amount or 0)

    # 这个不起做用了
    # @cash.setter
    # def cash(self, v):
    #     assert v < 0, "积分不能低于0"
    #     self.amount = v

    def send_cash(self, v=0):
        # 增加cash
        cash = self.cash
        # self.cash = cash + v
        v = cash + v
        assert v >= 0, f"积分不能低于0 ({v})"
        self.amount = v

    def do_giveup(self):
        self.giveup = True

    def is_giveup(self):
        return bool(self.giveup) == True

    def do_allin(self):
        self.allin  = True

    def is_allin(self):
        return bool(self.allin) == True

    # def is_sit()

class WechatGroupInfo(RunningInfo):
    def __init__(self, _id):
        super(WechatGroupInfo, self).__init__(mod="api", role="wechat", uid=_id)

    # def init(self):
    #     if self.exists():
    #         return
    #     # 从数据库中读出来
    #     log.info("即将从数据库加载", self)
    #     data = db_poker_funds[self.__uid__] or db_poker_makers[self.__uid__] or {}
    #     for k,v in data.items():
    #         # 跳过
    #         # if k in ["_id"]: continue
    #         setattr(self, k, v)
    #     self.refresh()

    def init_me(self):
        self.room = 0
        self.refresh()

    @property
    def room(self):
        return int(self.read("room") or "0")