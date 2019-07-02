#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/27 14:09
# @Author  : xxlaila
# @Site    : 
# @File    : config.py
# @Software: PyCharm

import os
#Wechat

Url='https://qyapi.weixin.qq.com/cgi-bin'
redis_host='127.0.0.1'
redis_port='6379'
redis_pass='123456'

env_dist = os.environ
corpid=os.environ.get('CORPID')
corpsecret=os.environ.get('CORPSECRET')
#print (os.getenv('CORPID'))
#print (os.environ.get('CORPSECRET'))

