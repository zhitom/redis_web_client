#!/usr/bin/env python
# coding:utf-8
import json
key={'cmd':'$cluster nodes','response':'aaa'}

keys=json.dumps(key)
keyojb=json.loads(keys)
print keyojb['cmd']
print keyojb['response']
k={}

a=['a1','a2']
print a[1]

