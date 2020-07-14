#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""事件控制初始化函数
    import本文件下其他所有py文件，

    定义事件处理函数，执行传来的参数名字的py文件,实现MessageType和操作名的映射

    Exp:event_handler_map[event_type].run(sc, parameters)，
event_type = 1 = login,则会执行login.run(sc,parameters).
"""

from pprint import pprint
import server.event_handler.login
import server.event_handler.send_message
import server.event_handler.register
import server.event_handler.resolve_friend_request
import server.event_handler.client_echo
import server.event_handler.add_friend
import server.event_handler.del_friend
import server.event_handler.join_room
import server.event_handler.create_room
import server.event_handler.query_room_users
import server.event_handler.bad
from common.message import MessageType

event_handler_map = {
    MessageType.login: login,
    MessageType.send_message: send_message,
    MessageType.register: register,
    MessageType.resolve_friend_request: resolve_friend_request,
    MessageType.client_echo: client_echo,
    MessageType.add_friend: add_friend,
    MessageType.del_friend: del_friend,
    MessageType.join_room: join_room,
    MessageType.create_room: create_room,
    MessageType.query_room_users: query_room_users,
    MessageType.bad: bad,
}


def handle_event(sc, event_type, parameters):
    event_handler_map[event_type].run(sc, parameters)
