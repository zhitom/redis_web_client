#!/usr/bin/env python
# coding:utf-8
__author__ = 'carey'
__date__ = '2017/12/25'

DEBUG = True

LOG_LEVEL = 'INFO'

# redis
base = {
    'servers': [
        {
            'index': 0,
            'name': 'redis0',
            'host': '10.0.20.203',
            'port': 8000,
            'password': '',
            'databases': 16
            # }, {
            #  'index': 1,
            #  'name': 'redis1',
            #  'host': '127.0.0.1',
            #  'port': 6379,
            #  'password': '',
            #  'databases': 16
        }
    ],
    'seperator': ':',
    'maxkeylen': 100
}
socket_timeout = 5
scan_batch = 10000  # scan 限制获取数据量
show_key_self_count = False
