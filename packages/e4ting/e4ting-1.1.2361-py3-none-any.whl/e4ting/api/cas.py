#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    [模块名]
    Add By :antiy chendejun@antiy.cn 2023-06-26 22:31:33
"""
import sys,os
import json,time
from pdb import set_trace as strace
from traceback  import format_exc as dumpstack
from textwrap import dedent
import requests

from e4ting       import log,util
from e4ting.cache import TokenCache

from casdoor import CasdoorSDK

certificate = '''-----BEGIN CERTIFICATE-----
MIIE3TCCAsWgAwIBAgIDAeJAMA0GCSqGSIb3DQEBCwUAMCgxDjAMBgNVBAoTBWFk
bWluMRYwFAYDVQQDEw1jZXJ0LWJ1aWx0LWluMB4XDTIzMDQxMDE0MzAwOVoXDTQz
MDQxMDE0MzAwOVowKDEOMAwGA1UEChMFYWRtaW4xFjAUBgNVBAMTDWNlcnQtYnVp
bHQtaW4wggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQC3PBMfE8sWv8Fx
jAkqN34cs8aYzQ/xVrPwxDQgCSf7qPfpgBUKhMH44Jw1BwyieacbbAw7ZfltCPOT
uCtDIFucrE/NIki+HLLQgomnyNxbrqfzUS4rpeJrkY/oo5PZegkwkz8sO9GWeuGN
HjZG3ruhGby8iZCH6B5RckkXdwaw9PTf52/yxH4OS9GUmcg18AWmH5bpXVP1hQQ7
bgHJCQ4UXti8MgmI1J+Hm3obLcETd7lO0v/IUtuHnvfQGCsSj/bFjhDyA0Vzsx0M
uXmvy74KwBoTo7nfhMWodx9NkaZCD2wwy2JsWu4iygoD1RwUVDLmZCNIAjDQaIbk
V3fK9DMEbd7/h/toz+6yCxeyAciD3I81e9xE0H+GjO1n9lUT+yRID39dEIbfmoQs
rR+AN4GIklsNKHkbgcCoQtvPZUfLznMBLugxPmQuh0Ri+KWW9hpi65yMkzA2Y4Fo
l0W7BJrCeSk+1Bm60gv0LWJl/wB5gxTRHGrM3TIbYZK87tATAH+x1MECrPwCRn4g
3BaaKBH53mYuqqVOojs7qUbixh1D/YxpxfodeEUOBS1U6tutsbiw0HAIeaNpl5R6
gYVI4czRgu0woR2qT904H3OI9Z6F4NknoGRmDJHN4gN+cCqSNR+XFV+BIVyoa99S
O51k8SzZX74hn6Vtt/DRDcRg0O0nXwIDAQABoxAwDjAMBgNVHRMBAf8EAjAAMA0G
CSqGSIb3DQEBCwUAA4ICAQBYeoEVB0mtRJfS0mIbqvr+3VEkhgUy6YmsufuxCDNX
4DTJ/ylOCZ6xpEuHwk++2EaAsC+jMfGYBx8HB7i94mk8M2BYi0dKHnw87S5OcpwZ
oGJ13Pv9iQTaQDn1WZeW6tIiVRygZaDyCMHufkkUcsTyf8nBEidV8efQmyDdnbjQ
xAF8dUk8PyP8sxL5oPhb74kZNmk4OQHoFHsxLEsVLVE0QdKNVzBSDu4bAbNphF00
PAjgvx5ukXuecrX3T3Vuqp9cHcokS27zjXeHMXe8cDgQ2T9OJrwhUgO114paZMXP
zPllnZMfG4OsTeFo8vHKPDfyIEwZTmm2eBMsqZbOUVIme/CWjsduAeCkaJFaaULJ
Fph1IPBqmwEOdDmuisqKJgNDG5wCBVpGmx//o4o3+pjENuFjlj657lLq1UW61/W/
Xy8pMzzBQsKAX1aU6U/qfMKqDKKu1HOL75I552nCnbuhWW8zOIqKRajKNeM3euAk
2Taxopj+pBeVxAGyYKBQPW+XPDWwUjvaIkb4qGxcHC0/v9Ust9l1VCxKslpJxQ4a
zeQbQ52lJfkGUsyC46vBuc6N62JqB7iEIrhz3J1oD/xA9sx8yhEyfvV61id1W9U8
aZMLftRT0pByHFctuICuUd/xmiuEdgMlTC6t0LsiKO6PMCgUFiCzQl+5Q+HVx6i6
1A==
-----END CERTIFICATE-----'''

class CasDoor():
    def __init__(self, refer="", client_ip=""):
        # self.code = code
        # self.token = token
        self.grant_type = "authorization_code"
        self.client_id = "api"
        self.client_secret = "e4ting"
        self.refer = refer # "http://auth.e4ting.cn"
        self.casdoor_host = "http://mycas.e4ting.cn"
        self.client_ip = client_ip

        self.sdk = CasdoorSDK(
            endpoint=self.casdoor_host,
            client_id=self.client_id,
            client_secret=self.client_secret,
            certificate=certificate,
            org_name='paozi',
            application_name='API',
        )

    @property
    def login_url(self):
        return "{self.casdoor_host}/login/oauth/authorize?client_id={self.client_id}&response_type=code&redirect_uri={self.refer}&scope=read&state=casdoor".format(self=self)

    def goto_login(self):
        payload = dict(code=302, url=self.login_url)
        return payload

    @util.redef_return(ret=False)
    def check_code(self, code):
        if not code:
            return False

        if TokenCache(code).exists():
            self.token = TokenCache(code).access_token
            return True

        payload = dict(
            grant_type=self.grant_type,
            client_id=self.client_id,
            client_secret=self.client_secret,
            code=code,
            redirect_uri=self.refer,
        )
        url = "{self.casdoor_host}/api/login/oauth/access_token".format(self=self)
        TokenCache.login_id
        # ret = util.HTTP().post(url, payload, headers={"Content-Type": "x-www-form-urlencoded"})
        res = requests.post(url, payload)
        ret = res.json()
        log.info(ret)
        if not "access_token" in ret:
            return False
        self.token = ret["access_token"]
        TokenCache(self.token).set(client_ip=self.client_ip, uptime=util.now(), **ret, **payload)
        TokenCache(code).set(client_ip=self.client_ip, uptime=util.now(), **ret, **payload)
        # from e4ting.task import Async
        # Async().get_user_detail(self.token, code)
        return True

    @util.redef_return(ret=False)
    def check_token(self):
        if not self.token:
            return False
        log.debug(self.token)
        # userinfo = self.sdk.parse_jwt_token(self.token)
        userinfo = self.get_userinfo(self.token)
        return bool(userinfo)

    @util.redef_return(ret={})
    def userinfo(self):
        info = self.sdk.parse_jwt_token(self.token)
        log.info(info)
        return {
            "uid" : info["name"],
            "username" : info["displayName"],
            "phone" : info["phone"],
            "email" : info["email"],
            "avatar" : info["avatar"],
            "type" : info["type"],
        }

    def get_userinfo(self, token):
        url = "{self.casdoor_host}/api/userinfo".format(self=self)
        ret = util.HTTP().get(url, _json=True, headers={"Authorization": "Bearer {token}".format(token=token)})
        log.debug(ret)
        if not ret:
            return False
        if ret.get("status", '') == 'error':
            return False
        return ret

    def get_user(self, token):
        url = "{self.casdoor_host}/api/get-account".format(self=self)
        ret = util.HTTP().get(url, _json=True, headers={"Authorization": "Bearer {token}".format(token=token)})
        log.info(ret)
        if not ret:
            return False
        return ret

if __name__ == "__main__":
    sdk = CasdoorSDK(
        endpoint='https://mycas.e4ting.cn',
        client_id='api',
        client_secret='e4ting',
        certificate=certificate,
        org_name='paozi',
        application_name='API',
    )
    # code = "addad03e6e30132f4df4"
    # token = TokenCache(code)
    payload = sdk.parse_jwt_token(token.access_token)
    util.log(payload)
    # strace()
    # sdk.get_oauth_token(code)