import io
import json

import pandas as pd
import numpy as np
import os
import shutil
from pyhive import hive
import pymysql
import pytz
import datetime
import time

from importers.common.config_util import BaseConfig


def split_str(s, sep, qualifier):
    """
    分割复杂字符串
     例如：'"sss,ss", userId,event,tismestamp,,"sss,ss",tismes,"sss,ss"'
     结果：['sss,ss', 'userId', 'event', 'tismestamp', '', 'sss,ss', 'tismes', 'sss,ss']
    :param s: 字符串
    :param sep: 分隔符
    :param qualifier: 文本限定符
    :return: List
    """
    if s is None or s.strip() == '':
        return []
    df = pd.read_csv(io.StringIO(s), sep=sep, quotechar=qualifier, header=None, na_filter=False)
    return np.array(df.where(df.notnull(), '')).tolist()[0]


def get_all_file(path):
    """
    获取目录下全部文件，包含子文件下的
    :param path: 目录或文件路径
    :return: [file_abs_path1,file_abs_path2,...]
    """
    res = []
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                res.append(os.path.join(root, name))
    else:
        res.append(path)
    return res


def remove_file(path):
    """
     删除Path.如果是文件路径直接删除文件；如果是目录，删除目录及目录下全部
    :param path: 目录或文件
    """
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    else:
        os.rmdir(path)


def create_dir(dir_str):
    """
     创建目录
    :param dir_str: 目录
    """
    if os.path.exists(dir_str) is False:
        os.makedirs(dir_str)


def time_str_to_timestamp_of_tz(time_str, format, timezone):
    """
     时间字符串转时间戳，带时区
    :param time_str:
    :param format:
    :param timezone:
    :return:
    """
    tz = pytz.timezone(timezone)
    dt = datetime.datetime.strptime(time_str, format)
    t = tz.localize(dt).astimezone(pytz.utc)
    return int(time.mktime(t.utctimetuple())) - time.timezone


def time_format(time_str, timezone):
    """
     支持多种格式的时间字符串转时间戳，带时区
    :param time_str: 时间字符串
    :param timezone: 时区
    :return: time_formatted: 毫秒时间戳
    """
    str_length = len(time_str)
    if time_str.isdigit():
        # 主要是为了支撑一个产品功能，不然无法分辨秒和毫秒
        if str_length == 10:
            time_formatted = int(time_str) * 1000
        elif str_length in [12, 13]:
            time_formatted = int(time_str)

    else:
        if str_length == 10:
            format = get_format("%Y-%m-%d", time_str)
        elif str_length == 19:
            format = get_format("%Y-%m-%d %H:%M:%S", time_str)
        elif str_length == 23:
            format = get_format("%Y-%m-%d %H:%M:%S.%f", time_str)

        time_formatted = time_str_to_timestamp_of_tz(time_str, format, timezone) * 1000

    return time_formatted


def get_format(format, time_str):
    """
     根据传进来的时间来获取具体的时间格式
    :param format: 时间格式
    :param time_str: 时间字符串
    :return: format: 原先时间的格式
    """
    delimiters = ["-", "/"]
    delimiter = time_str[4:5]
    if delimiters.__contains__(delimiter):
        format = format[:2] + delimiter + format[3:5] + delimiter + format[6:]

    return format


def mysql_connect(user, password, host, port):
    """
     获取mysql连接
    :param user: mysql用户名
    :param password: mysql密码
    :param host: mysql Host
    :param port: mysql 端口号
    :return:
    """
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        charset='utf8',
        passwd=password,
        db='information_schema'
    )


def hive_connect(host, port, user):
    """
     获取hive连接
    :param host: hive Host
    :param port: hive 端口号
    :param user: hive用户名
    :return:
    """
    return hive.Connection(host=host, port=port, username=user, database='default')


def getVariables(dataCenter):
    """
     获取变量标识符列表
    :param dataCenter: getdataCenterEventVariables、getdataCenterUserVariables
    :return:标识符列表
    """
    vars = dataCenter
    var_list = []
    for var in vars:
        var_list.append(var['key'])
    return var_list


def getItemVariables(dataCenter):
    """
     获取主体标识符列表
    :param dataCenter: getdataCenterEventVariables、getdataCenterUserVariables
    :return:标识符列表
    """
    data = json.loads(json.dumps(dataCenter))
    var_list = []
    for item in data:
        for attr in item['attributes']:
            if attr['isPrimaryKey']:
                var_list.append(attr['key'])
    return var_list


def date_range(start_date, end_date, timezone=BaseConfig.timezone):
    """
     遍历一段时间范围，[start_date,end_date)，左闭右开。
    :param start_date 开始时间
    :param end_date 结束时间
    """
    dateTimeFormatter = '%Y-%m-%d'
    time_list = []
    tz = pytz.timezone(timezone)
    start = datetime.datetime.strptime(start_date, dateTimeFormatter).astimezone(tz)
    end = datetime.datetime.strptime(end_date, dateTimeFormatter).astimezone(tz)
    s = start.date()
    e = end.date()
    for i in range((e - s).days):
        day = s + datetime.timedelta(days=i)
        timeArray = time.strptime(str(day), dateTimeFormatter)
        timestamp = (int(time.mktime(timeArray)) - time.timezone) * 1000
        time_list.append(timestamp)
    return time_list
