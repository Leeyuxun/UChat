#!/usr/bin/env python
# -*- coding:utf-8 -*-

from server.memory import *

"""广播每个secure_channel对象发送信息类型和参数"""
def broadcast(message_type, parameters):
    for sc in scs:
        sc.send(message_type, parameters)