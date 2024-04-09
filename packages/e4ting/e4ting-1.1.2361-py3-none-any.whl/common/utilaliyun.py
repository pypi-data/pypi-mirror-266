#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    [模块名]
    Add By :test test@gmail.com 2022-01-11 23:00:28
"""
import sys,os
import json
from pdb import set_trace as strace
from traceback  import format_exc as dumpstack

# from aliyunsdkcore.client import AcsClient
# from aliyunsdkcore.acs_exception.exceptions import ClientException
# from aliyunsdkcore.acs_exception.exceptions import ServerException
# from aliyunsdkdomain.request.v20180129.QueryDomainListRequest import QueryDomainListRequest
# from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
# from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
# from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest

from . import util

class AliDomainAPI():
    def __init__(self, ali_id, key, zone):
        from aliyunsdkcore.client import AcsClient
        self.client = AcsClient(ali_id, key, zone)

    def list(self):
        # 列举域名
        from aliyunsdkdomain.request.v20180129.QueryDomainListRequest import QueryDomainListRequest
        req = QueryDomainListRequest()
        req.set_accept_format('json')

        req.set_PageNum(1)
        req.set_PageSize(50)

        response = self.client.do_action_with_exception(req)
        response = json.loads(response.decode())
        # for _ in response["Data"]["Domain"]:
        #     util.log("[{DomainName}] {InstanceId} -> {ExpirationDate}".format(**_), level='info')

        # util.log(json.dumps(response, indent=1))
        return response["Data"]["Domain"]

    def records(self, domain):
        # def details(domain='e4ting.cn'):
        from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
        request = DescribeDomainRecordsRequest()
        request.set_accept_format('json')
        request.set_DomainName(domain)
        request.set_PageSize(500)

        response = self.client.do_action_with_exception(request)
        response = json.loads(response.decode())
        # util.log(json.dumps(response, indent=1))

        # info = {}
        # for _ in response["DomainRecords"]["Record"]:
        #     util.log("[{DomainName}]{Type}: {RR}.{DomainName} -> {Value}".format(**_), level='debug')
        #     info[_["RR"]] = _
        ret = response["DomainRecords"]["Record"]
        return [
                {
                    "name": _["RR"],
                    "value": _["Value"],
                    "ttl": _["TTL"],
                    "type": _["Type"],
                    "id": _["RecordId"],
                    "domain": _["DomainName"],
                } for _ in ret
            ]

    def add_A_record(self):
        # 添加A记录
        pass

    def add_c_name(self):
        # 添加cname记录
        pass

class NamesiloDomainAPI():
    def __init__(self, TOKEN):
        from namesilo.core import NameSilo
        self.client = NameSilo(token=TOKEN, sandbox=False)

    def list(self):
        domains = self.client.list_domains()
        if type(domains) is str:
            return [domains]
        return domains

    def records(self, domain):
        """
        distance: "0"
        host: "www.e4t.buzz"
        record_id: "e944175bd298a3ea7817e91a72c6e843"
        ttl: "3600"
        type: "A"
        value: "141.164.47.11"
        """
        ret = self.client.list_dns_records(domain)
        return [{
                    "name": _["host"],
                    "value": _["value"],
                    "ttl": _["ttl"],
                    "type": _["type"],
                    "id": _["record_id"],
                    "domain": _["host"],
                } for _ in ret ]

    def add_A_record(self):
        # 添加A记录
        pass

    def add_c_name(self):
        # 添加cname记录
        pass




