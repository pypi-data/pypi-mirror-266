#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    [模块名]
    Add By :e4ting chendejun@antiy.cn 2022-08-23 15:04:14
"""
import sys,os
from pdb import set_trace as strace
from traceback  import format_exc as dumpstack

import json,time
import websocket
import random

def on_message(ws, message):
    # print("### message ###")
    # print(ws)
    payload = json.loads(message)
    print(payload)
    tid = payload["tid"]
    # howlong = random.randint(0, 5)
    # print("将等待 ", howlong)
    # time.sleep(howlong)
    ws.send(json.dumps({"code":200, "tid":tid, "msg":payload}))

def on_error(ws, error):
    print("""error""")
    print(error)

def on_close(ws, *args):
    print(ws, args)
    # strace()
    print("### closed ###")

def main():
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
                                "ws://172.24.0.6:80/api/v3/socket/123",
                                # "ws://www.e4ting.cn/api/v1/socket/conn/123",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                header={"Sec-WebSocket-Protocol": "e4ting"}
                                )

    ws.run_forever()

if __name__ == '__main__':
    main()
