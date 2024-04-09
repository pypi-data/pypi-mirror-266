#!/bin/env python3
# -*- coding:utf-8 -*-

# import pymongo
from e4ting.db  import mongodb
import json
from pdb        import set_trace  as strace
from traceback  import format_exc as dumpstack

from e4ting import log

# from .dbpoker import *

db_requests         = mongodb(host='mongo.com', db="data",    table="requests" , level="debug")
db_data_token       = mongodb(host='mongo.com', db="data",    table="token")
db_ssh              = mongodb(host='mongo.com', db="data",    table="ssh")
db_users            = mongodb(host='mongo.com', db="data",    table="users")
db_menus            = mongodb(host='mongo.com', db="data",    table="menus")
db_roles            = mongodb(host='mongo.com', db="data",    table="roles")
db_res              = mongodb(host='mongo.com', db="data",    table="resource")
db_login_record     = mongodb(host='mongo.com', db="data",    table="login_record")
db_folders          = mongodb(host='mongo.com', db="data",    table="folders")
db_startups         = mongodb(host='mongo.com', db="data",    table="启动记录")
db_data_medias      = mongodb(host='mongo.com', db="data",    table="medias")
db_data_resumes     = mongodb(host='mongo.com', db="data",    table="resumes")
db_data_files       = mongodb(host='mongo.com', db="data",    table="files")

db_data_wsrecord    = mongodb(host='mongo.com', db="data",    table="wsrecord")

# 库存模块列表
db_botnet_modules   = mongodb(host='mongo.com', db="botnet",  table="modules")

# 注册记录
db_botnet_registers = mongodb(host='mongo.com', db="botnet", table="注册记录")

# websocket连接记录
db_botnet_connects  = mongodb(host='mongo.com', db="botnet", table="ws连接记录")

# 设备加载了哪些模块
db_botnet_dev_mods  = mongodb(host='mongo.com', db="botnet",  table="dev_mods")

# 设备列表
db_botnet_clients   = mongodb(host='mongo.com', db="botnet",  table="clients")

# SSH列表
db_botnet_sshs   = mongodb(host='mongo.com', db="botnet",  table="sshs")

# 全局Mac列表
db_botnet_macs    = mongodb(host='mongo.com', db="botnet",  table="macs")
db_botnet_mac_link= mongodb(host='mongo.com', db="botnet",  table="macs_links")


# 从chrome采集上来的用户列表
db_botnet_chrome_u  = mongodb(host='mongo.com', db="botnet",  table="chrome_users")

# 从chrome采集上来的cookie列表
db_botnet_chrome_c  = mongodb(host='mongo.com', db="botnet",  table="chrome_cookies")

# 定时任务列表
db_crontabs         = mongodb(host='mongo.com', db="botnet",  table="crontabs")

db_budejie_robots   = mongodb(host='mongo.com', db="budejie", table="robots")
db_budejie_users    = mongodb(host='mongo.com', db="budejie", table="users")
db_budejie_proxys   = mongodb(host='mongo.com', db="budejie", table="proxys")

db_proxys           = mongodb(host='mongo.com', db="common",  table="proxys")
db_IPs              = mongodb(host='mongo.com', db="common",  table="IPs")

db_jianshu_topics   = mongodb(host='mongo.com', db="jianshu", table="topics")

db_DNS_rules        = mongodb(host='mongo.com', db="dns",     table="rules")
db_DNS_action       = mongodb(host='mongo.com', db="dns",     table="action")
db_DNS_record       = mongodb(host='mongo.com', db="dns",     table="record")

db_eatinglist       = mongodb(host='mongo.com', db="eating",  table="eatinglist")
db_eating_action    = mongodb(host='mongo.com', db="eating",  table="action")

db_licongfiles      = mongodb(host='mongo.com', db="licong",  table="files")
db_licongcompanys   = mongodb(host='mongo.com', db="licong",  table="companys")

db_budejie_proxys   = mongodb(host='mongo.com', db="budejie", table="proxys")
db_budejie_topics   = mongodb(host='mongo.com', db="budejie", table="topics")

db_JP_XL_DEVS       = mongodb(host='mongo.com', db="JP",      table="XL")
db_JP_FT_DEVS       = mongodb(host='mongo.com', db="JP",      table="FT")
db_JP_YL_DEVS       = mongodb(host='mongo.com', db="JP",      table="YL")
db_JP_JS            = mongodb(host='mongo.com', db="JP",      table="JS")
db_JP_MHT_BIG       = mongodb(host='mongo.com', db="JP",      table="MHT_BIG")
db_JP_CDHZ          = mongodb(host='mongo.com', db="JP",      table="CDHZ")

db_JP_XL_SNS        = mongodb(host='mongo.com', db="common",  table="XL_SN")

db_little_rules     = mongodb(host='mongo.com', db="LittleData", table="datarules")
db_little_middle    = mongodb(host='mongo.com', db="LittleData", table="middle_dada")
db_little_links     = mongodb(host='mongo.com', db="LittleData", table="links")

db_onething_tobdata = mongodb(host='vm.db.com', db="onething", table="ToBData")
db_onething_tob1day = mongodb(host='vm.db.com', db="onething", table="ToB1day")
db_onething_tob1day_dk = mongodb(host='vm.db.com', db="onething", table="ToB1day_DK")
db_onething_tob1day_zqb = mongodb(host='vm.db.com', db="onething", table="ToB1day_zqb")
db_onething_tobname = mongodb(host='vm.db.com', db="onething", table="ToBClients")

# 网心云线上激活
db_onething_active = mongodb(host='vm.db.com', db="onething", table="active")

db_onething_public_ip_map = mongodb(host='vm.db.com', db="onething", table="public_ip_map")
db_onething_tob_mon       = mongodb(host='vm.db.com', db="onething", table="ToBMonth")

db_onething_reconciliation = mongodb(host='mongo.com', db="onething", table="reconciliation")

db_onething_tob_robot     = mongodb(host='mongo.com', db="onething", table="tob_robot")
db_onething_tob_permission= mongodb(host='mongo.com', db="onething", table="tob_permission")

db_onething_horizon_tables= mongodb(host='mongo.com', db="onething", table="horizon_tables")

# QQ 和 微信不共用一套ID命名规则，所以两者不会发生冲突，可以存在同一张表中
# 群
db_chats_groups  = mongodb(host='mongo.com', db="chats", table="groups")
# 成员
db_chats_members = mongodb(host='mongo.com', db="chats", table="members")
# 群 & 成员 的关系
db_chats_links   = mongodb(host='mongo.com', db="chats", table="links")
# 账号密码保存表
db_chats_accounts= mongodb(host='mongo.com', db="chats", table="accounts")
# 产品类型
db_chats_ptype   = mongodb(host='mongo.com', db="chats", table="ptype")
# 产品 和 竞品 放在一个表里
db_chats_product = mongodb(host='mongo.com', db="chats", table="product")
# # 竞品
# db_chats_enemy   = mongodb(host='mongo.com', db="chats", table="enemy")
# 消息处理 拦截和自动回复放在一个表里
db_chats_actions = mongodb(host='mongo.com', db="chats", table="actions")


db_raw_messages = mongodb(host='mongo.com', db="onething", table="qq")

db_chats_word_frequency = mongodb(host='mongo.com', db="chats", table="_word_frequency")
db_chats_messages    = mongodb(host='mongo.com', db="chats", table="messages")
db_chats_wechatmsgs  = mongodb(host='mongo.com', db="chats", table="wechatmsgs", level="debug")
db_chats_group_count = mongodb(host='mongo.com', db="chats", table="_group_count")
db_chats_member_count= mongodb(host='mongo.com', db="chats", table="_member_count")

# 连接池
db_chats_config      = mongodb(host='mongo.com', db="chats", table="pool_config")

# 主页面板配置
db_data_layout      = mongodb(host='mongo.com', db="data", table="layout")

# 备案数据关联库
db_icp_data         = mongodb(host='mongo.com', db="icp",  table="data")
db_icp_beian        = mongodb(host='mongo.com', db="icp",  table="beian.miit.gov.cn")

class TABLE():
    def __init__(self, db, table):
        self.db = db
        self.table = table

    def __get__(self, instance, owner):
        return mongodb(host='mongo.com', db=self.db,  table=self.table)

class DB():
    # 不这么做在 alpine 系统中会出现诡异现象

    templates  = TABLE(db="data",  table="templates")
    robots     = TABLE(db="data",  table="robots")
    webhook    = TABLE(db="data",  table="webhook")

    person     = TABLE(db="data",  table="person")
    JS         = TABLE(db="JP",    table="JS")
    clients    = TABLE(db="botnet",  table="clients")
    statistics = TABLE(db="data",  table="statistics")



