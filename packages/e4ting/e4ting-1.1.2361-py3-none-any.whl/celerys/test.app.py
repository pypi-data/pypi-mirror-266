#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    [模块名]
    Add By :e4ting chendejun@antiy.cn 2022-08-23 15:04:14
"""

import json
import random

from celerys.tasks.server import emit
from celerys.tasks import server

# python.start_ws()

def progress(callback, iterable, desc="正在处理", key=lambda x:""):
    """ 处理进度条 """
    from tqdm import tqdm
    # ret = []
    pbar = tqdm(iterable, ncols=125)
    # 这个函数性能极差，将近150倍的样子 Add By cdj 2020-10-16 15:42:12
    pbar.set_description("{}".format(desc))
    ret = list(map(callback, pbar))
    return ret

# for i in range(100):
#     ret = python.emit("test", 123)
#     print (f"[{i}] {ret}")

progress(lambda x:server.emit(json.dumps({"test":x, "tid":random.randint(0, 1000000)}), 123), range(1000))
