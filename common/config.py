#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""获取配置文件信息"""

import json
from pprint import pprint

with open('config.json') as config_file:
    config = json.load(config_file)


def get_config():
    return config