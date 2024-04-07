#!/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright (c) 2020 growingio.com, Inc.  All Rights Reserved

import ftplib
import json
import csv
import time

from importers.common.common_util import time_format
from importers.common.config_util import FTPConfig, BaseConfig, ApiConfig

from collections import Counter

from importers.common.log_util import logger, my_logger
from importers.data_import.data_model import DataEvent


def check_sv_header_col_value(attr_header_list):
    """
       校验CSV/TSV格式数据头-固定列数的值
    """
    error_list = []

    required_cols = ['event', 'timestamp']

    for col in required_cols:
        if col not in attr_header_list:
            error_list.append(col)

    return error_list


def check_sv_header_col_count(attr_header_list, data_header_list):
    """
       校验CSV/TSV格式数据头-列数
    """
    if len(attr_header_list) != len(data_header_list):
        return False


def check_sv_header_col_order(attr_header_list, data_header_list):
    """
       校验CSV/TSV格式数据头-不为''的顺序
    """
    try:
        for i in range(len(attr_header_list)):
            if attr_header_list[i] != '' and attr_header_list[i] != data_header_list[i]:
                return False
    except Exception:
        return False


def check_sv_col_duplicate(data_list):
    """
       校验CSV/TSV格式数据列名是否重复
    """
    for item in Counter([i for i in data_list if i != '']).items():
        if item[1] > 1:
            return item[0]


def check_csv_header_col_count(cols, line, separator):
    # 创建一个CSV reader
    csv_reader = csv.reader([line], delimiter=separator, quotechar='"')
    columns = next(csv_reader)
    if len(columns) != len(cols):
        return False

    for col_index, col_value in enumerate(columns):
        try:
            json.loads(col_value)
            return True  # 如果成功解析JSON数据，则返回True
        except json.JSONDecodeError:
            continue

    return False


def add_header_to_file(file_path, header_columns, separator):
    """
    向文件添加表头。

    :param file_path: 要修改的文件路径。
    :param header_columns: 表头列名的列表。
    :param separator: 列分隔符。
    """
    with open(file_path, 'r', encoding='utf8') as file:
        original_content = file.read()

    with open(file_path, 'w', encoding='utf8') as file:
        header = separator.join(header_columns) + '\n'
        file.write(header + original_content)


def remove_first_line_from_csv(original_file, output_file=None):
    """
    删除向文件添加的表头。
    """
    if output_file is None:
        output_file = original_file

    with open(original_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(lines[1:])


def replace_first_line_with_header(file_path, header_columns, separator):
    """
    替换文件的第一行为新的表头。

    :param file_path: 要修改的文件路径。
    :param header_columns: 新表头列名的列表。
    :param separator: 列分隔符。
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 生成新的表头
    header = separator.join(header_columns) + '\n'
    # 替换第一行
    lines[0] = header
    # 将修改后的内容写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)


def mkd_file():
    """
    FTP创建目录
    :target_directory: 目标目录
    :return:
    """
    ftp = ftplib.FTP()
    ftp.connect(host=FTPConfig.host, port=int(FTPConfig.port))
    ftp.login(user=FTPConfig.user, passwd=FTPConfig.password)
    target_directory = ftp.mkd('/jobs/importer/' + str(int(round(time.time() * 1000))))
    ftp.close()
    return target_directory


def put_file(file_list, target_directory, max_retries=3):
    """
    FTP上传文件，并在失败时重试
    :param file_list: 待上传文件列表
    :param target_directory: 目标目录
    :param max_retries: 最大重试次数
    :return:
    """
    ftp_start_time = time.time()
    retries = 0
    while retries <= max_retries:
        try:
            ftp = ftplib.FTP()
            ftp.connect(host=FTPConfig.host, port=int(FTPConfig.port))
            ftp.login(user=FTPConfig.user, passwd=FTPConfig.password)
            connected = True
        except Exception as e:
            logger.error(f'连接FTP服务器失败: {e}')
            retries += 1
            connected = False
            if retries <= max_retries:
                my_logger.info(f'重试连接FTP服务器, 尝试次数: {retries}')
                time.sleep(5)
            else:
                logger.error('达到最大重试次数，连接失败。')
                exit(-1)

        if connected:
            # 上传文件
            for file in file_list:
                upload_retries = 0
                while upload_retries <= max_retries:
                    try:
                        file_splits = file.split('/')
                        simple_name = file_splits[len(file_splits) - 1]
                        with open(file, 'rb') as fp:
                            cmd = 'STOR %s/%s' % (target_directory, simple_name)
                            ftp.storbinary(cmd, fp)
                        break
                    except Exception as e:
                        logger.error(f'上传文件{file}至FTP失败: {e}')
                        upload_retries += 1
                        if upload_retries > max_retries:
                            logger.error(f'文件{file}达到最大重试次数，上传失败。')
                            exit(-1)
                        else:
                            my_logger.info(f'重试上传文件{file}, 尝试次数: {upload_retries}')
                            time.sleep(5)
            break
    ftp.quit()
    ftp_end_time = time.time()
    ftp_cost_time = ftp_end_time - ftp_start_time
    my_logger.info("文件上传至FTP耗时:%.3f秒" % ftp_cost_time)


def delete_file(file_list, target_directory):
    ftp = ftplib.FTP()
    ftp.connect(host=FTPConfig.host, port=int(FTPConfig.port))
    ftp.login(user=FTPConfig.user, passwd=FTPConfig.password)
    for file in file_list:
        file_splits = file.split('/')
        simple_name = file_splits[len(file_splits) - 1]
        ftp.delete('%s/%s' % (target_directory, simple_name))
    ftp.close()


def extract_and_validate_data(json_data):
    error_message = ""
    # 检查 userKey 字段，如果存在且值为 $notuser，则不需要 userId
    if json_data.get('userKey') != '$notuser' and 'userId' not in json_data:
        error_message += f"缺少userId需指定\n若传主体事件,则数据需字段userKey, 且值为‘$notuser’\n"
        return None, error_message
    # 确保 event,timestamp 字段存在
    elif 'event' not in json_data or 'timestamp' not in json_data:
        error_message += "event或timestamp字段不存在\n"
        return None, error_message

        # 提取字段并创建 DataEvent 对象
    data_event = DataEvent(
        userId=json_data.get('userId', ''),
        event=json_data['event'],
        timestamp=json_data['timestamp'],
        attrs=json_data.get('attrs', {}),
        userKey=json_data.get('userKey', ''),
        eventId=json_data.get('eventId', None),
        dataSourceId=json_data.get('dataSourceId', None)
    )
    return data_event, error_message


def validate_data_event(data_event, eventStart, eventEnd, cstm_keys, cstm_attr_keys):
    error_message = ""
    normal = True

    event = data_event.event
    var_keys = cstm_keys.get(event)
    attr_all = BaseConfig.attr_all

    if event in ['$exit', '$bounce']:
        normal = False
        error_message += f"事件[{event}]为t+1离线计算生成，不支持导入\n"

    if var_keys is None:
        normal = False
        error_message += f"事件[{event}]在GIO平台未定义，请先在系统中定义\n"

    if not str(var_keys).startswith("$"):
        if hasattr(data_event, 'attrs'):
            attrs_customize_error = []
            attrs_bind_error = []
            for attr in data_event.attrs:
                if attr not in attr_all:
                    # 事件属性
                    if attr not in cstm_attr_keys:
                        attrs_customize_error.append(attr)
                    # 事件绑定属性
                    elif var_keys is not None and attr not in var_keys and attr is not None:
                        attrs_bind_error.append(attr)
            if len(attrs_customize_error) > 0 or len(attrs_bind_error) > 0:
                normal = False
                if len(attrs_customize_error) > 0:
                    error_message += f"事件属性[{attrs_customize_error}]在GIO平台未定义，请先在系统中定义\n"
                if len(attrs_bind_error) > 0:
                    error_message += f"不存在事件属性[{attrs_bind_error}]与事件[{event}]的绑定关系\n"

    elif str(var_keys).startswith("$") and var_keys is not None:
        if str(var_keys) not in ["$page", "$visit"]:
            normal = False
            error_message += f"预置事件只支持$page，$visit\n"
        else:
            if hasattr(data_event, 'attrs'):
                attrs_customize_error = []
                attrs_bind_error = []
                for attr in data_event.attrs:
                    if attr not in attr_all:
                        # 事件属性
                        if attr not in cstm_attr_keys:
                            attrs_customize_error.append(attr)
                    # 事件绑定属性
                    elif attr not in var_keys and attr is not None:
                        attrs_bind_error.append(attr)
                if len(attrs_customize_error) > 0 or len(attrs_bind_error) > 0:
                    normal = False
                    if len(attrs_customize_error) > 0:
                        error_message += f"事件属性[{attrs_customize_error}]在GIO平台未定义，请先在系统中定义\n"
                    if len(attrs_bind_error) > 0:
                        error_message += f"不存在事件属性[{attrs_bind_error}]与事件[{event}]的绑定关系\n"

    if not hasattr(data_event, 'timestamp'):
        normal = False
        error_message += "缺少timestamp需指定\n"
    else:
        timestamp = 0
        try:
            timestamp = time_format(str(data_event.timestamp), BaseConfig.timezone)
        except Exception:
            normal = False
            error_message += "timestamp格式错误，请参考数据导入帮助文档\n"

        if (timestamp < eventStart or timestamp > eventEnd) and timestamp != 0:
            normal = False
            error_message += "timestamp时间范围不合法\n"

    return normal, error_message


def count_lines_in_file(paths):
    total_lines = 0
    for path in paths:
        with open(path, 'r') as file:
            lines = sum(1 for line in file)
        total_lines += lines

    return total_lines


def portal_token(new_token):
    """更新 token"""
    ApiConfig.update_token(new_token)
