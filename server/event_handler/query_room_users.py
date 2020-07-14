#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""控制数据库开始执行群聊中发消息的操作
    query_room_users_result操作码会发给客户端，客户端接收之后经过判断识别
根据target_type为1判断为群聊，刷新群聊窗口
"""

from pprint import pprint
from common.message import MessageType
from server.broadcast import broadcast
import server.memory
from common.util import md5
from server.util import database
from server.util import add_target_type


def run(sc, parameters):
    user_id = server.memory.sc_to_user_id[sc]
    if not database.in_room(user_id, parameters):
        sc.send(MessageType.general_failure, '不在群里')
        return
    sc.send(MessageType.query_room_users_result, [database.get_room_members(parameters), parameters])
