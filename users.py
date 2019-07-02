#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/27 14:09
# @Author  : xxlaila
# @Site    : 
# @File    : users.py
# @Software: PyCharm

import sys
import json
import requests
from alarm.config import *
from lib import jenkinsci
import redis
import pypinyin

header = {'content-type': 'application/json'}
reload(sys)
sys.setdefaultencoding('utf8')

class WechatAPi():

    def __init__(self):
        pass

    def redis_connect(self):
        r = redis.Redis(host=redis_host, password=redis_pass, port=redis_port)
        return r

    def getwechattoken(self):
        """
        获取token
        :return:
        """
        reUrl = '{}/gettoken?corpid={}&corpsecret={}'.format(Url, corpid, corpsecret)
        try:
            req = requests.get(reUrl)
            Jsondata = json.loads(req.content)
            if Jsondata['errcode'] == 0:
                return Jsondata['access_token']
            else:
                return Jsondata['errmsg']
        except Exception as e:
            return str(e)

    def upload_to_redis(self):
        """
        数据缓存redis 1小时
        :return:
        """
        token = self.getwechattoken()
        session = self.redis_connect()
        res = session.get("wechat")
        if res:
            new_res = json.loads(res)
            tokens = new_res["token"]
            wechat_token = tokens
        else:
            token = self.getwechattoken()
            data = {"token": token}
            new_data = json.dumps(data)
            session.set("wechat", new_data)
            session.expire("wechat", 3600)
            res = session.get("wechat")
            new_res = json.loads(res)
            tokens = new_res["token"]
            wechat_token = tokens

        return wechat_token


    def getDepartment(self):
        """
        获取部门列表
        :return:
        """
        restustoken = self.upload_to_redis()
        if not restustoken:
            print("获取token失败")
        reUrl = '{}/department/list?access_token={}'.format(Url, restustoken)
        try:
            req = requests.get(reUrl)
            Jsondata = json.loads(req.content)
            if Jsondata['errcode'] == 0:
                return Jsondata['department']
            else:
                return False
        except Exception as e:
            return str(e)

    def getDeparUsers(self):
        """
        获取部门成员信息
        :return:
        """
        restustoken = self.upload_to_redis()
        if not [restustoken]:
            print("获取token或部门失败")
        try:
            department_id = 1
            reUrl = '{}/user/list?access_token={}&department_id={}&fetch_child=1'.format(Url, restustoken,
                                                                                         department_id)
            req = requests.get(reUrl)
            Jsondata = json.loads(req.content)
            if Jsondata['errcode'] == 0:
                return Jsondata['userlist']
        except Exception as e:
            return str(e)

    def getDepatmentId(self):
        """
        获取部门名称和id
        :return:
        """
        data = {}
        Departments = self.getDepartment()
        for Department in Departments:
            DepartmentId = Department['id']
            DepartmentName = Department['name']
            data[DepartmentName] = DepartmentId

        return data

    def MessageBuild(self):
        """
        根据触发人和前后端信息生成不同的数据，进行组装
        :return:
        """
        datas ={}
        user_lists = self.getDeparUsers()
        Depat = self.getDepatmentId()
        data_result = content
        results = ("job_name: %s" % data_result['JOB_NAME'] + '\n'"build_num: %s" % data_result['build_num'] + '\n'
                "build_node: %s" % data_result['build_node'] + '\n'"job_status: %s" % data_result['job_status'] + '\n'
                "developers: %s" % data_result['developers'] +'\n'"commit_message: %s" % data_result['commit_info'] + '\n'
                "commit_version: %s" % data_result['commit_version'] +'\n'"git_url: %s" % data_result['git_url'] + '\n'
                "job_build_url: %s" % data_result['job_build_url'] + '\n'"info: %s" % data_result['info'])
        names = data_result['developers']
        if names in ['dev', 'test', 'admin']:
            if 'dev.com' in data_result['JOB_NAME']:
                name = "前端组".decode('utf8')
                if name in Depat:
                    Deparid = Depat[name]
                else:
                    Deparid =18
            else:
                name = "后端组"
                if name in Depat:
                    Deparid = Depat[name]
                else:
                    Deparid = 18

            datas = {
                    "touser": Deparid,
                    "toparty": Deparid,
                    "msgtype": "text",
                    "agentid": 1000002,
                    "text": {
                        "content": results
                    },
                    "safe": 0
                }
        else:
            name_str = pypinyin.pinyin(names.decode('utf-8'), style=pypinyin.NORMAL)
            for user_list in user_lists:
                wechat_users = user_list['name']
                if names in wechat_users:
                    userid = user_list['userid']
                    datas = {
                        "touser": userid,
                        "msgtype": "text",
                        "agentid": 1000002,
                        "text": {
                            "content": results
                        },
                        "safe": 0
                    }
        return datas

    def SendMessage(self):
        restustoken = self.upload_to_redis()
        data = self.MessageBuild()
        reUrl = '{}/message/send?access_token={}'.format(Url, restustoken)
        conf_r = requests.post(reUrl, json.dumps(data), headers=header)
        config_result = json.loads(conf_r.content)
        print (config_result)

if __name__ == '__main__':
    values = sys.argv[1:]
    Jekins_aa = jenkinsci.JenkinsApi(values[0], values[1], values[2])
    content = Jekins_aa.altem_infos()
    wechat_a = WechatAPi()
    wechat_a.SendMessage()