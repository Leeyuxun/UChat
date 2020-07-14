#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    定义实现数据库操作的各种函数
"""

import sqlite3
from pprint import pprint
from server.memory import *

conn = sqlite3.connect('server/database.db', isolation_level=None)


def get_cursor():
    return conn.cursor()


def commit():
    return conn.commit()

def get_user(user_id):
    c = get_cursor()
    fields = ['id', 'username','ip','port']
    row = c.execute('SELECT ' + ','.join(fields) + ' FROM users WHERE id=?', [user_id]).fetchall()
    if len(row) == 0:
        return None
    else:
        user = dict(zip(fields, row[0]))
        user['online'] = user_id in user_id_to_sc
        return user


"""获取user_id是被加方的所有行"""
def get_pending_friend_request(user_id):
    c = get_cursor()
    users = []
    rows = c.execute('SELECT from_user_id FROM friends WHERE to_user_id=? AND NOT accepted', [user_id]).fetchall()
    for row in rows:
        uid = row[0]
        # pprint([uid, type(uid)])
        users.append(get_user(uid))
    return users

"""获取user_id是申请方的所有行"""
def get_friends(user_id):
    c = get_cursor()
    users = []
    rows = c.execute('SELECT to_user_id FROM friends WHERE from_user_id=? AND accepted', [user_id]).fetchall()
    for row in rows:
        uid = row[0]
        # pprint([uid, type(uid)])
        users.append(get_user(uid))
    return users


def get_user_rooms(user_id):
    c = get_cursor()
    rooms = []
    rows = c.execute('SELECT room_id FROM room_user WHERE user_id=?', [user_id]).fetchall()
    for row in rows:
        room_id = row[0]
        rooms.append(get_room(room_id))
    return rooms


def get_user_rooms_id(user_id):
    c = get_cursor()
    rooms = []
    rows = c.execute('SELECT room_id FROM room_user WHERE user_id=?', [user_id]).fetchall()
    for row in rows:
        room_id = row[0]
        rooms.append(room_id)
    return rooms


def is_friend_with(from_user_id, to_user_id):
    c = get_cursor()
    r = c.execute('SELECT 1 FROM friends WHERE from_user_id=? AND to_user_id=? AND accepted=1',
                  [from_user_id, to_user_id]).fetchall()
    return len(r) > 0


def get_room(room_id):
    c = get_cursor()
    fields = ['id', 'room_name']
    row = c.execute('SELECT ' + ','.join(fields) + ' FROM rooms WHERE id=?', [room_id]).fetchall()
    if len(row) == 0:
        return None
    else:
        room = dict(zip(fields, row[0]))
        return room


def in_room(user_id, room_id):
    c = get_cursor()
    r = c.execute('SELECT 1 FROM room_user WHERE user_id=? AND room_id=? ',
                  [user_id, room_id]).fetchall()
    return len(r) > 0


def add_to_room(user_id, room_id):
    c = get_cursor()
    r = c.execute('INSERT INTO room_user (user_id,room_id) VALUES (?,?) ',
                  [user_id, room_id])


def get_room_members_id(room_id):
    return list(map(lambda x: x[0], get_cursor().execute('SELECT user_id FROM room_user WHERE room_id=?',
                                                         [room_id]).fetchall()))


def get_room_members(room_id):
    # [id,  online, username]
    return list(map(lambda x: [x[0], x[1], x[0] in user_id_to_sc, x[2]], get_cursor().execute(
        'SELECT user_id,username FROM room_user LEFT JOIN users ON users.id=user_id WHERE room_id=?',
        [room_id]).fetchall()))

"""将发送方向接收方发送的信息存入数据库,用于历史消息重发"""
def add_to_chat_history(user_id, target_id, target_type, data, sent):
    c = get_cursor()
    c.execute('INSERT INTO chat_history (user_id,target_id,target_type,data,sent) VALUES (?,?,?,?,?)',
              [user_id, target_id, target_type, data, sent])
    return c.lastrowid


# [[data:bytes,sent:int]]
"""获取某用户的历史消息"""
def get_chat_history(user_id):
    c = get_cursor()
    ret = list(map(lambda x: [bytearray(x[0]), x[1]],
                   c.execute('SELECT data,sent FROM chat_history WHERE user_id=?',
                             [user_id]).fetchall()))
    c = get_cursor()
    c.execute('UPDATE chat_history SET sent=1 WHERE user_id=?', [user_id])
    return ret
