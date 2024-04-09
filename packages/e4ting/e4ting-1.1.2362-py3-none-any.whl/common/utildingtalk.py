#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    [模块名]
    Add By : cdj <e4ting@qq.com> 2021-12-13 10:36:21
"""
import os,sys
import time,json
from traceback  import format_exc as dumpstack
from pdb import set_trace as strace


# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
# from common              import util

import os,sys
import time,json
from traceback  import format_exc as dumpstack
from pdb import set_trace as strace

# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
# from common              import util
import util
from util import HTTP,log,now
from textwrap import dedent

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from jinja2 import Template

from common import util
from modules.api.utilconsul import ConsulAPI

class Robot(object):
    dtalk_config = ConsulAPI(path="e4ting/robot/dtalk")

    def __init__(self, token):
        self.url = token

    def get_token(cls, name="common"):
        if not name:
            return cls.dtalk_config.get("common")
        return cls.dtalk_config.get(name)

    def push_msg(self, title="toB跑量播报", text="# toB跑量播报 \n* test"):
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title" : title,
                "text"  : text,
            },
            "at": {
                "isAtAll": False,
            }
        }
        ret = HTTP().post(self.url, payload)
        log(ret)
        return ret

    def send_report(self, data):
        template = dedent("""# {name}
                             * **推送时间：**{date}
                             * **总共：**{total}
                             * **成功：**{ok}
                             * **失败：**[{fail}](http://ove.e4ting.cn:8081/onething/wechat/pusher)
                             * **未绑定：**[{unbind}](http://ove.e4ting.cn:8081/onething/wechat/pusher)
                             * **操作员：**{user}
                    """)
        ret = template.format(**data)
        log(ret)
        return self.push_msg("微信推送结果", ret)


if __name__ == '__main__':
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    dtalk = DingTalk(url="https://oapi.dingtalk.com/robot/send?access_token=5e1edb25add7223a10785bc9c6d7c9e3ccb8c6ef9cda0261a3d45f0ca7e6034f")
    dtalk.send(title="测试", text={"时间":util.now()})
