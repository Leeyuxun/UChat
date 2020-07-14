#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""出现错误操作使程序走向可处理除0操作"""

from pprint import pprint
from common.message import MessageType
from server.broadcast import broadcast
import server.memory
from common.util import md5
from server.util import database


def run(sc, parameters):
    a = 1 / 0