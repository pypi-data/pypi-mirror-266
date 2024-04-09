#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    [模块名]
    Add By :antiy chendejun@antiy.cn 2022-11-11 10:24:31
    api_url: 'https://qyapi.weixin.qq.com/cgi-bin/'
    corp_id: 'ww51a1103db0f0bd1e'
    api_secret: 'qZaBLm_3wsJZMasYAKKTxu25JkiHHA3QXlkhWBP7vjE'

    机器人token
    https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=5165c29d-3224-4ad0-a0a8-fd7882e81062
    开发文档
    https://developer.work.weixin.qq.com/document/path/91770

"""
import sys,os
from pdb import set_trace as strace
from traceback  import format_exc as dumpstack

from modules.common import util
# from modules.api.spug import SPUG,SpugAPI
# from modules.common.utilmongo import db_submit_dev
# from modules.miner.crypt import check_id

from modules.common.utilcache  import DeviceCache,UserCache
# from modules.common.utilrecord import save_dev_submit,save_device_info,get_device_info,get_device_income
# from celery_task.py_tasks.python import get_miner_devs
from textwrap import dedent
from jinja2 import Template

class WeiXinRobot(util.HTTP):

    def __init__(self, webhook="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=5165c29d-3224-4ad0-a0a8-fd7882e81062"):
        self.webhook = webhook
        super(WeiXinRobot, self).__init__()

    def format_msg(self, title='', **data):
        # 格式化消息
        template = Template(dedent("""
                ## {{ title }}
                {% for name,value in data.items() %}
                > **{{ name }}** : <font color="info">{{ value }}</font>
                {% endfor %}
                """))
        return template.render(title=title, data=data)

    def format_txt(self, title='', **data):
        # 格式化消息
        template = Template(dedent("""
                {{ title }}
                {% for name,value in data.items() %}
                {{ name }} : {{ value }}
                {% endfor %}
                """))
        return template.render(title=title, data=data)

    """{
        "msgtype": "text",
        "text": {
            "content": "广州今日天气：29度，大部分多云，降雨概率：60%",
            "mentioned_list":["wangqing","@all"],
            "mentioned_mobile_list":["13800001111","@all"]
        }
    }"""

    def send_md(self, msg):
        # 发送消息
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": msg
            }
        }
        ret = self.post(self.webhook, payload)
        # util.log(ret)
        if ret["errcode"] != 0:
            util.log(ret)
            return False
        return True

    def send_txt(self, msg):
        # 发送消息
        payload = {
            "msgtype": "text",
            "text": {
                "content": msg,
                # "mentioned_list":["wangqing","@all"],
                # "mentioned_mobile_list":["13800001111","@all"]
            }
        }
        ret = self.post(self.webhook, payload)
        if ret["errcode"] != 0:
            util.log(ret)
            return False
        return True

    def notify(self, title='', **data):
        data = self.format_msg(title, **data)
        return self.send_md(data)

    def notify_txt(self, title='', **data):
        data = self.format_txt(title, **data)
        return self.send_txt(data)

def main():
    robot = WeiXinRobot()
    # strace()
    # data = robot.format_msg(title="发送测试", **{"指标1":"100%","指标2":"99%"})
    # robot.send_md(data)

    robot.notify_txt(title=f"跑量（{util.day_N(1)}）", **{"总跑量":"1.01G","设备":"2台","用户数":"2"})

if __name__ == '__main__':
    main()



