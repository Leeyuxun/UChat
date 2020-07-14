#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    服务器控制数据库注册，删除了空白字符并将英文字符小写。
    并在本地将之前的用户证书更新，写入用户username和邮箱
"""

from pprint import pprint
from common.message import MessageType
from server.broadcast import broadcast
import server.memory
from common.util import md5

from server.util import database


def run(sc, parameters):
    parameters[0] = parameters[0].strip().lower()
    c = database.get_cursor()
    r = c.execute('SELECT * from users where username=?', [parameters[0]])
    rows = r.fetchall()
    if len(rows) > 0:
        sc.send(MessageType.username_taken)
        return

    #用户ip获取，命名证书，获取信息更新证书，服务端证书也会用自己的个人信息更新
    ip =str(parameters[3])
    certname = ip + "_cert.pem"
    with open(certname, 'rb') as f:
        context = f.read()
        sp = context.split()
        f.close()
    with open(certname,'wb') as f:
        f.write((str(parameters[0]) + ' ' +str(parameters[2]) + " " + str(sp[2])).encode())
        f.close()

    c = database.get_cursor()
    c.execute('INSERT into users (username,password,email,ip,port,sex,age) values (?,?,?,?,?,?,?)',
              [parameters[0], md5(parameters[1]), parameters[2], parameters[3], parameters[4], parameters[5], parameters[6]])
    sc.send(MessageType.register_successful, c.lastrowid)

