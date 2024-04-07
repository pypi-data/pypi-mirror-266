import json

import requests

from importers.common.common_util import date_range
from importers.common.config_util import ApiConfig
from importers.common.log_util import logger, my_logger
import time

from importers.meta.data_center import updateClearUserJobStatus, getClearUsers, checkUserExits, createClearUser


def clearUserData(execute):
    if str(execute).upper() == 'TRUE':
        users = getClearUsers()
        projectIds = set()
        for id, value in users.items():
            projectIds.add(value)
            assert updateClearUserJobStatus(id) == 'RUNNING'
        for id in projectIds:
            headers = {'Content-Type': 'application/json', 'Authorization': ApiConfig.token}
            ftpPath = '/clearuser/' + str(int(round(time.time() * 1000)))
            body = {'pipelineDefinitionId': 'ClearUserPipeline', 'identity': 'gio',
                    'conf': {'$ftpPath': ftpPath, '$projectId': id}}
            r = requests.post(ApiConfig.oauth2_uri + '/data-server/scheduler/pipeline/running', headers=headers,
                              data=json.dumps(body))
            if r.status_code == 200:
                my_logger.info("提交清理用户删除离线任务")
                my_logger.info("待删除用户数据存放FTP位置为:{}".format('/ftp/admin' + ftpPath))
    elif str(execute).upper() == 'FALSE':
        users = getClearUsers()
        for user in users:
            assert updateClearUserJobStatus(user) == 'RUNNING'
        my_logger.info("等待天任务清理用户删除任务")
        my_logger.info("待删除用户数据将存放FTP位置为:{}".format('/ftp/admin/clearuser'))


def clearUserMeta(userids):
    users = str(userids).split(",")
    for user in users:
        if checkUserExits(user):
            continue
        else:
            logger.error("用户:{} 不存在！".format(user))
            exit(-1)
    for user in users:
        createClearUser(user)
    my_logger.info("添加待删除用户完成，用户为:{}。".format(userids))


def globalMetricJob(start_time, end_time):
    headers = {'Content-Type': 'application/json', 'Authorization': ApiConfig.token}
    time_list = date_range(start_time, end_time)
    if len(time_list) > 30:
        logger.error("超出一个月任务需要重跑计算")
        exit(-1)
    for time in time_list:
        body = {'pipelineDefinitionId': 'GlobalMetricDailyPipeline', 'identity': 'gio', 'conf': {'$startPos': time}}
        r = requests.post(ApiConfig.oauth2_uri + '/data-server/scheduler/pipeline/running', headers=headers,
                          data=json.dumps(body))
        if r.status_code != 200:
            logger.error("startPos:{}, 任务提交失败".format(time))
            exit(-1)
    my_logger.info("任务提交完成")
