#!/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright (c) 2020 growingio.com, Inc.  All Rights Reserved
import csv
import json

import pandas as pd

from importers.data_import.data_model import UserVariablesSv, UserVariablesJson
from importers.data_import.data_format_util import *
from importers.common import http_util
from importers.common.common_util import getVariables
from importers.common.log_util import logger, my_logger
from json.decoder import JSONDecodeError
from importers.meta.data_center import getdataCenterUserVariables, getImportJobStatus, trigger_job


def user_variables_import(args):
    """
       用户属性导入，按数据格式处理
    """
    # Step one: 校验事件数据基础参数，并预处理
    # 1. 数据源是否为属性
    ds = args.get('datasource_id')
    if 'USER_PROPERTY' in ds[1]:
        args['datasource_id'] = ds[1]['USER_PROPERTY']
    else:
        logger.error("数据源不属于用户属性类型")
        exit(-1)
    # Step one: 按数据格式处理
    f = str(args.get('format'))
    if 'JSON'.__eq__(f):
        user_variables_import_send(
            UserVariablesJson(name=args.get('m'), path=args.get('path'), debug=args.get('debug'), format=f,
                              datasourceId=args.get('datasource_id'), jobName=args.get('jobName'),
                              clear=args.get('clear'))
        )
    elif 'CSV'.__eq__(f):
        separator = args.get("separator")
        separator = ',' if separator == '' else separator
        user_variables_import_send(
            UserVariablesSv(name=args.get('m'), path=args.get('path'), debug=args.get('debug'), format=f,
                            datasourceId=args.get('datasource_id'), jobName=args.get('jobName')
                            , attributes=args.get('attributes'), separator=separator,
                            skipHeader=args.get('skip_header'), clear=args.get('clear'))
        )
    elif 'TSV'.__eq__(f):
        separator = args.get("separator")
        separator = '\t' if separator == '' else separator
        user_variables_import_send(
            UserVariablesSv(name=args.get('m'), path=args.get('path'), debug=args.get('debug'), format=f,
                            datasourceId=args.get('datasource_id'), jobName=args.get('jobName'),
                            attributes=args.get('attributes'), separator=separator, skipHeader=args.get('skip_header'),
                            clear=args.get('clear'))
        )


def sv_import_prepare_process(attributes, paths, skip_header, separator, qualifier):
    """
      1.校验数据基本信息
      2.SV格式数据转换为Json格式导入
    """
    # Step 1: 校验有无attributes,有无重复列名
    if attributes is None:
        logger.error(f"[-attr/--attributes]参数值不存在")
        exit(-1)

    cols = str(attributes).split(',')
    duplicate_col = check_sv_col_duplicate(cols)
    if duplicate_col is not None:
        logger.error(f"[-attr/--attributes]出现重复列值[{duplicate_col}]")
        exit(-1)

    keys = getVariables(getdataCenterUserVariables())
    count = 0
    for path in paths:
        if skip_header:
            replace_first_line_with_header(path, cols, separator)
        # 读取文件第一行，与预期表头比较
        with open(path, 'r', encoding='utf8') as f:
            first_line = f.readline().strip()
            expected_header = separator.join(cols)
            if first_line != expected_header:
                add_header_to_file(path, cols, separator)

        skip_header = True
        with open(path, 'r', encoding='utf8') as f:
            for line in f:
                count += 1
                # Step 2: 数据列是否一致
                line = line.replace('\n', '').replace('\\t', '\t')
                line_normal = True
                if check_sv_header_col_count(cols, line.split(separator)) is False:
                    if not check_csv_header_col_count(cols, line, separator):
                        remove_first_line_from_csv(path)
                        logger.error(
                            f"第{count}行:导入文件[{path}]的列数和参数值列数不一致\n请检查文件分隔符，并通过参数[-sep]指定")
                        return False
                if not line_normal:
                    continue
                # Step 3: 校验数据列是否一致
        df = pd.read_csv(path, sep=separator, header=0 if skip_header else None,
                         names=cols if not skip_header else None, quotechar=qualifier)
        # 校验表头
        if skip_header and not all(col in df.columns for col in cols):
            logger.error(f"文件[{path}]的列名与预期不匹配")
            exit(-1)
        # 逐行处理数据
        for index, row in df.iterrows():
            col_value = row.to_dict()
            # 处理 userKey 逻辑
            user_key = col_value.get('userKey', '')
            if 'userKey' in cols and user_key == '$notuser':
                logger.error(f"文件[{path}]数据[{row.to_string()}]中的userKey值不合法")
                exit(-1)
            # 构建属性字典
            attrs = {key: value for key, value in col_value.items() if
                     len(str(value)) != 0 and key not in ['userKey', 'userId']}
            # 校验用户属性是否在 GIO 平台定义
            undefined_keys = [key for key in attrs if not key.startswith('$') and key not in keys]
            if undefined_keys:
                logger.error(f"文件[{path}]数据[{row.to_string()}]用户属性{undefined_keys}在GIO平台未定义")
                exit(-1)
    my_logger.info(f"本次共校验[{count}]行数据")
    return True


def user_variables_import_send(userVariables):
    """
       用户属性导入，Json格式数据处理
    """
    # Step 1: 执行Debug
    f = userVariables.format

    if userVariables.debug:
        if 'JSON'.__eq__(f):
            if user_variables_debug_process(userVariables.path) is not True:
                logger.error("Debug校验未通过")
                exit(-1)
        else:
            if sv_import_prepare_process(attributes=userVariables.attributes,
                                         paths=userVariables.path,
                                         skip_header=userVariables.skipHeader,
                                         separator=userVariables.separator,
                                         qualifier=userVariables.qualifier) is not True:
                logger.error("Debug校验未通过")
                exit(-1)
    else:
        lines_count = count_lines_in_file(userVariables.path)
        my_logger.info(f"本次共导入[{lines_count}]行数据")

    if len(str(userVariables.jobName)) == 0 or userVariables.jobName is None:
        jobName = f"Python_user_{time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))}"
    else:
        jobName = userVariables.jobName
    # Step 2: 创建导入任务
    if 'JSON'.__eq__(f):
        job_info = create_task_json(userVariables.datasourceId, jobName)
    else:
        job_info = create_task_sv(userVariables.datasourceId, jobName, userVariables.separator)
    # 任务名重复时，获取不到job信息时，程序直接结束
    if job_info is None:
        logger.error("job_info为空，无法创建导入任务")
        exit(-1)
    else:
        my_logger.info(f"创建导入任务: {job_info}")
    direct = job_info['argument']['directory']
    # Step 3: 上传数据到FTP
    my_logger.info(f"文件开始上传至FTP")
    put_file(userVariables.path, direct)

    # Step 4: 启动导入任务
    start_time = time.time()
    trigger_job(job_info['id'])
    my_logger.info(f"开始执行导入任务")
    flag = True
    while flag:
        eventImportJob = getImportJobStatus(job_info['id'])
        if eventImportJob is not None:
            stage = eventImportJob['stage']
            error = eventImportJob['error']
            if stage is not None and stage.__eq__("FINISH"):
                end_time = time.time()
                cost_time = end_time - start_time
                my_logger.info("导入成功")
                delete_file(userVariables.path, direct)
                my_logger.info("执行导入任务耗时:%.3f秒" % cost_time)
                flag = False
            elif stage is not None and stage.__eq__("ERROR"):
                end_time = time.time()
                cost_time = end_time - start_time
                if error is not None:
                    message = error.get('message', 'No message available')
                else:
                    message = 'Error object is None'
                logger.error(f"导入失败,错误信息为[ {message} ] \n FTP文件路径: {direct}")
                my_logger.info("执行导入任务耗时:%.3f秒" % cost_time)
                exit(-1)
        if flag:
            my_logger.info(f"等待任务完成......")
            time.sleep(10)


def create_task_json(ds, name):
    """
           创建任务,允许用户自定义更改任务名称
        """
    if len(str(name)) == 0:
        body = '''{ "operationName": "createEventImportJob", "variables": { "fileType":"ftp", "timeRange":"", 
        "tunnelId": "%s", "createType":"PYTHON" }, "query": "mutation createEventImportJob($tunnelId: HashId!, 
        $timeRange: String, $fileType: String, $createType: String) { createEventImportJob(tunnelId: $tunnelId, 
        timeRange: $timeRange,fileType: $fileType, createType: $createType) { id name argument { directory __typename 
        } __typename } }" }''' % ds
    else:
        body = '''{ "operationName":"createEventImportJob", "variables":{ "fileType":"ftp", "tunnelId":"%s", 
        "timeRange":"", "name":"%s", "createType":"PYTHON" }, "query":"mutation createEventImportJob($name: String, 
        $tunnelId: HashId!, $timeRange: String, $fileType: String, $createType: String) { createEventImportJob(name: 
        $name, tunnelId: $tunnelId, timeRange: $timeRange, fileType: $fileType, createType: $createType) { id name 
        argument { directory __typename } __typename } }" }''' % (ds, name)
    resp = http_util.send_graphql_post(body.encode('utf-8'))
    try:
        return resp['createEventImportJob']
    except TypeError:
        logger.error("自定义任务名称已存在！")


def create_task_sv(ds, name, separator):
    """
           创建任务,允许用户自定义更改任务名称
    """
    separator = separator.replace("\t", "\\\\t")
    if len(str(name)) == 0:
        body = '''{ "operationName": "createEventImportJobV2", "variables": { "fileType":"csv", "timeRange":"", 
        "tunnelId": "%s", "createType":"PYTHON", "csvSeparator":"%s" }, "query": "mutation createEventImportJobV2(
        $tunnelId: HashId!, $timeRange: String, $fileType: String, $createType: String, $csvSeparator: String) { 
        createEventImportJobV2(tunnelId: $tunnelId, timeRange: $timeRange,fileType: $fileType, createType: 
        $createType, csvSeparator: $csvSeparator) { id name argument { directory __typename } __typename } }" }''' % (
            ds, separator)
    else:
        body = '''{ "operationName":"createEventImportJobV2", "variables":{ "fileType":"csv", "tunnelId":"%s", 
        "timeRange":"", "name":"%s", "createType":"PYTHON", "csvSeparator":"%s" }, "query":"mutation 
        createEventImportJobV2($name: String, $tunnelId: HashId!, $timeRange: String, $fileType: String, $createType: 
        String, $csvSeparator: String) { createEventImportJobV2(name: $name, tunnelId: $tunnelId, timeRange: 
        $timeRange, fileType: $fileType, createType: $createType, csvSeparator:$csvSeparator) { id name argument { 
        directory __typename } __typename } }" }''' % (ds, name, separator)
    resp = http_util.send_graphql_post(body.encode('utf-8'))
    try:
        return resp['createEventImportJobV2']
    except TypeError:
        logger.error("自定义任务名称已存在！")


def user_variables_debug_process(paths):
    """
       用户属性导入Debug
       1、校验有无userId
       2、校验用户属性(条件:是否是平台内置和是否定义)
    """
    keys = getVariables(getdataCenterUserVariables())
    count = 0
    dict_count = 0
    error_count = 0
    error_dict = {}
    for path in paths:
        with open(path, 'r', encoding='utf8') as f:
            for line in f:
                count = count + 1
                line = line.replace('\n', '')
                if not line == '':
                    normal = True
                    error_message = ""
                    try:
                        data_dictionary = json.loads(line)
                        # userId或anonymousId
                        if 'userId' not in data_dictionary:
                            normal = False
                            error_message += f"userId不存在\n"

                        if 'userKey' in data_dictionary:
                            if data_dictionary['userKey'] == '$notuser':
                                normal = False
                                error_message += f"用户属性导入不支持用户身份为‘$notuser’\n"

                        # 用户属性
                        if 'attrs' in data_dictionary:
                            if not isinstance(data_dictionary['attrs'], dict):
                                normal = False
                                error_message += f"attrs数据格式不对\n"

                            for key in data_dictionary['attrs']:
                                if data_dictionary['attrs'][key] is None:
                                    normal = False
                                    error_message += f"用户属性[{key}]的值为NULL,请检查原始数据\n"

                                if key not in keys:
                                    normal = False
                                    error_message += f"用户属性[{key}]在GIO平台未定义\n"

                    except JSONDecodeError:
                        normal = False
                        error_message += f"非JSON格式\n"

                    if not normal:
                        error_hash = hash(error_message)
                        if error_hash not in error_dict:
                            error_dict[error_hash] = error_message
                            logger.error(f"第{count}行:文件[{path}]数据[{line}],\n"
                                         f"{error_message}")
                            dict_count += 1
                        error_count += 1
                    if count % 500000 == 0:
                        my_logger.info(f"已经校验{count}条数据......")

                    if dict_count >= 10000:
                        logger.error("数据内容错误条数已经超过 10000 条, 请先修正数据 ")
                        exit(-1)
                else:
                    logger.warn(f"第{count}行为空，跳过该行")
        f.close()

    if error_count == 0:
        my_logger.info(f"本次共校验[{count}]行数据")
        return True
    else:
        my_logger.info(f"本次共校验[{count}]行数据,其中校验失败[{error_count}]行数据, 包含[{dict_count}]种错误类型，具体错误内容看上方日志详情")
        return False
