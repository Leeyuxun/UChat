#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""操作数据库删除好友"""

from pprint import pprint
from common.message import MessageType
from server.broadcast import broadcast
import server.memory
from common.util import md5
from server.util import database
from server.memory import *


def run(sc, parameters):
    user_id = sc_to_user_id[sc]
    # parameters = username
    c = database.get_cursor()
    username = parameters.strip().lower()
   # print(user_id)
    r = c.execute('SELECT id from users where username=?', [username]).fetchall()
    #print(r[0][0])
    #异常条件判断
    if len(r) == 0:
        sc.send(MessageType.del_friend_result, [False, '用户名不存在'])
        return

    uid = r[0][0]

    if uid == user_id:
        sc.send(MessageType.del_friend_result, [False, '不能删除自己'])
        return

    c = database.get_cursor()
    r = c.execute('SELECT 1 from friends where from_user_id=? and to_user_id=? and accepted=1', [user_id, uid]).fetchall()
    #判断对方是否已经是自己的好友了
    if len(r) == 0:
        sc.send(MessageType.del_friend_result, [False, '该用户还不是您的好友'])
        return
    #对方是你的好友
    if len(r) != 0:
        #删除操作
        c = database.get_cursor()
        c.execute('delete from friends where from_user_id=? and to_user_id=? and accepted=1', [uid, user_id]).fetchall()
        c.execute('delete from friends where from_user_id=? and to_user_id=? and accepted=1', [user_id, uid]).fetchall()

        sc.send(MessageType.del_friend_result, [True, ''])
        sc.send(MessageType.del_info, database.get_user(uid))

        #如果要删除的好友在线，将他的好友列表中将我删除的操作码发送给服务器
        if uid in user_id_to_sc:
            user_id_to_sc[uid].send(MessageType.del_info, database.get_user(user_id))
    return

