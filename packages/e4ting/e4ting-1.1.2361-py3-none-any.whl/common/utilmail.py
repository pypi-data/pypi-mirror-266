#!/bin/env python3
# -*- coding:utf-8 -*-
"""
    [模块名]
    Add By : cdj <e4ting@qq.com> 2021-09-17 15:58:23
"""
import os,sys
import time,json
from traceback  import format_exc as dumpstack
from pdb import set_trace as strace

import poplib
import sys
from importlib import reload
from email.parser import Parser
from email.parser import BytesParser
from email.header import decode_header
from email.utils import parseaddr
import email.iterators

# import util

class Mail():
    def __init__(self, index=0, _id="", lines=[]):
        self.index = index
        self.lines = lines
        self._id   = _id
        self.init()

    def addr(self, value):
        hdr, addr = parseaddr(value)
        # name = decode_str(addr)
        # value = name + ' < ' + addr + ' > '
        return addr

    @property
    def content(self):
        self.text = ''
        for part in self.msg.walk():
            filename = part.get_filename()
            content_type = part.get_content_type()
            charset = guess_charset(part)
            if filename:
                continue
                # filename = decode_str(filename)
                # data = part.get_payload(decode = True)
                # if filename != None or filename != '':
                #     print('Accessory: ' + filename)
                #     # savefile(filename, data, mypath)
                #     # print(data)
            else:
                email_content_type = ''
                # if content_type == 'text/plain':
                #     email_content_type = 'text'
                # elif content_type == 'text/html':
                #     email_content_type = 'html'
                if charset:
                    self.text = part.get_payload(decode=True).decode(charset)
                # print(content_type + ' ' + self.text)
        return self.text.strip()

    def init(self):
        self.msg = Parser().parsestr(
                '\r\n'.join(
                        [
                            e.decode()
                                for e in self.lines
                        ]
                    )
            )
        self.froms   = self.addr(self.msg.get("From", ''))
        self.to      = self.addr(self.msg.get("To", ''))
        self.subject = decode_str(self.msg.get("Subject", ''))
        # print(self.From, self.To, self.Subject)

    # def get(self):
    #     self

class EMail():
    def __init__(self, email="test@qq.com", passwd=""):
        self.email = email
        self.passwd = passwd
        self.pop3_server = self._pop3()

    def _pop3(self):
        tail = self.email.split("@")[1]
        return f"pop.{tail}"

    def login(self):
        self.server = poplib.POP3_SSL(self.pop3_server, 995)
        #print(server.getwelcome())
        self.server.user(self.email)
        self.server.pass_(self.passwd)
        # print('邮件数: %s 总大小 : %s' % self.server.stat())

    def start(self, page=1, size=10):
        return (page - 1) * size

    def end(self, page=1, size=10):
        return page * size

    def list(self, page=1, size=10):
        # strace()
        resp, mails, objects = self.server.list()
        print(f"共 {len(mails)} 封邮件")
        mails = mails[::-1][self.start(page, size):self.end(page, size)]
        num   = len(mails)
        # self.mails = [Mail(num - index, _, self.server.retr(num - index)[1]) for index,_ in enumerate(mails)]
        # return self.mails

    def __iter__(self):
        self.next = 0
        resp, mails, objects = self.server.list()
        self.mails = mails[::-1]
        self.num   = len(self.mails)
        return self

    def __next__(self):
        _ = self.mails[ self.next ]
        index = self.num - self.next
        self.next += 1
        # index=0, _id="", lines=[]
        return Mail( index=index,
                     _id=_,
                     lines=self.server.retr(index)[1]
                    )

    # def __del__(self):
    #     if hasattr(self, "server"):
    #         self.server.quit()

#解析消息头中的字符串
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

#将邮件附件或内容保存至文件
#即邮件中的附件数据写入附件文件
def savefile(filename, data, path):
    try:
        filepath = path + filename
        print('Save as: ' + filepath)
        f = open(filepath, 'wb')
    except:
        print(filepath + ' open failed')
        #f.close()
    else:
        f.write(data)
        f.close()

#获取邮件的字符编码，首先在message中寻找编码，如果没有，就在header的Content-Type中寻找
def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos+8:].strip()
    return charset

def get_code(text):
    # import jieba
    # strace()
    ret = text.split("验证码是")
    # print(ret)
    return ret[1]

def main():
    emails = EMail(email="chendejun@onething.net", passwd="P@ssw0rd.C0m")
    emails.login()
    # emails.list()
    for mail in emails:
        if "跳板机验证码" in mail.subject:
            code = get_code(mail.content)
            print(code, end="")
            # strace()
            break
    return

if __name__ == '__main__':
    main()
