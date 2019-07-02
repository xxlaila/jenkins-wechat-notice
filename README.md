# jenkins-wechat-notice

### jenkins企业微信告警
```
1、研发人员提交代码到gitlab自动触发jenkins，jenkins编译完成后，根据提交人员，自动拉取企业微信的用户id，把编译信息通过企业微信
发送给研发人员，支持公共的独立告警job，需要传递JOB_NAME。
2、job带有环境环境参数
```

### 设置变量
```
需要设置系统变量
CORPID='xxxxx'
CORPSECRET='xxxxxxxxxxxxxxx'
```
