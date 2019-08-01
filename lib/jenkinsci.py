#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/27 11:57
# @Author  : xxlaila
# @Site    : 
# @File    : jenkins
# @Software: PyCharm

from jenkinsapi.jenkins import Jenkins
import sys,re,json


class JenkinsApi():

    def __init__(self, ProjectName, env, JOB_NAME):
        self.env = env
        if self.env in ['dev', 'test', 'demo']:
            self.url = "http://ci.dev.com"
            self.username = "admin"
            self.password = "123456"
        self.ProjectName = ProjectName
        self.job_name = JOB_NAME
        self.server = self.connect()

    def connect(self):
        server= Jenkins(self.url, username=self.username, password=self.password)
        return server

    def get_job_details(self):
        """
        获取jenkinsjob,匹配
        :return:
        """
        server = self.connect()
        job_lists = server.has_job(self.job_name)
        if job_lists:
            job_instance = server.get_job(self.job_name)
        else:
            job_instance = None
            exit(-1)

        return job_instance


    def get_job_good_build(self):
        """
        提取job的编译号
        :return:
        """
        build_num = self.get_job_details().get_last_build()
        return build_num

    def get_job_status(self):
        """
        job状态
        :return:
        """
        status = self.get_job_good_build()
        job_status = status.get_status()
        return job_status

    def get_runn_status(self):
        """
        是否正在运行
        :return:
        """
        runn_status = self.get_job_details().is_running()
        return runn_status

    def get_enab_status(self):
        """
        job是否被启用
        :return:
        """
        enab_status = self.get_job_details().is_enabled()
        return enab_status

    def get_cons_status(self):
        """
        输出编译信息
        :return:
        """
        status = self.get_job_good_build()
        cons_status = status.get_console()
        return cons_status

    def get_developers(self):
        """
        代码提交人
        :return:
        """
        #developer = {}
        status = self.get_job_good_build()
        developers = status.get_changeset_items()
        Started = status.get_console()
        str_name = re.match("Started by (.*)", Started)
        developers = str_name.group(1)
        developer = developers.split(' ')[-1]

        return developer

    def get_job_number(self):
        """
        job 的mun号
        :return:
        """
        job_status = self.get_job_details().get_last_buildnumber()
        return job_status

    def get_job_url(self):
        """
        ci job 的url
        :return:
        """
        job_urls = self.get_job_details().url
        number = self.get_job_number()
        job_url = job_urls + str(number)
        return job_url

    def altem_infos(self):
        """
        企业微信告警
        :return:
        """
        job_names = self.get_job_details()
        build_num = job_names.get_last_build_or_none()
        if build_num is None:
            print("ci无编译记录，请重新触发")
            exit(-1)
        else:
            job_number = job_names.get_last_buildnumber()
            cons_status = build_num.get_console()
            job_build_num = job_names.get_last_build()
            job_build_url = self.get_job_url()

            str_name = re.match("Started by (.*)", cons_status)
            developers = str_name.group(1)
            developer = developers.split(' ')[-1]
            # developer = pypinyin.pinyin(developer_name, style=pypinyin.NORMAL)

            str_build_nodes = re.findall("Building remotely on (.*)", cons_status)
            build_nodes = " ".join(str_build_nodes).split(' ')[0]

            str_git_url = re.findall("Fetching upstream changes from (.*)", cons_status)
            git_url = str_git_url[0]

            str_commit_mess = re.findall("Commit message: (.*)", cons_status)
            commit_mess = str_commit_mess[0]

            str_commit_version = re.findall("Checking out Revision (.+?) \(.*\)", cons_status)
            commit_version = str_commit_version[0]
            job_status = build_num.get_status()
            if job_status != "SUCCESS":
                contents = cons_status.split('\n')[-20:]
                consul_result = ''
                for content in contents:
                    consul_result += content + '\n'
            else:
                consul_result = None

            jenkins_info = {'JOB_NAME': self.job_name, 'build_num': job_number, 'developers': developer,
                            'job_status': job_status, 'build_node': build_nodes, 'git_url': git_url,
                            'commit_info': commit_mess, 'commit_version': commit_version, 'info': consul_result,
                            'job_build_url': job_build_url}

            return jenkins_info