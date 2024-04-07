#!/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright (c) 2020 growingio.com, Inc.  All Rights Reserved

import json
import os
from json.decoder import JSONDecodeError

import pandas as pd

from importers.common import http_util
from importers.common.common_util import time_str_to_timestamp_of_tz
from importers.common.config_util import BaseConfig
from importers.common.log_util import logger, my_logger
from importers.data_import.data_format_util import *
from importers.data_import.data_model import AdsData, AdsEventsCv, AdsEventsJson
from importers.meta.data_center import getImportJobStatus, trigger_job

ONE_DAY_MILLISECOND = 86400 * 1000  # 1天(24小时)毫秒值


def ads_import(args):
    """
    广告数据导入，按数据格式处理
    """
    # Step one: 校验事件数据基础参数，并预处理
    # 1. 校验时间
    event_start = args.get("event_start")
    if event_start is None:
        logger.error("[-s/--event_start]参数值未指定")
        exit(-1)
    event_end = args.get("event_end")
    if event_end is None:
        logger.error("[-e/--event_end]参数值未指定")
        exit(-1)
    try:
        event_start = (
            time_str_to_timestamp_of_tz(event_start, "%Y-%m-%d", BaseConfig.timezone)
            * 1000
        )
        event_end = (
            time_str_to_timestamp_of_tz(event_end, "%Y-%m-%d", BaseConfig.timezone)
            * 1000
            + ONE_DAY_MILLISECOND
        )
    except (TypeError, ValueError):
        logger.error("[-s/--event_start]或[-e/--event_end]时间参数格式不对,格式为:YYYY-MM-DD")
        exit(-1)
    # 2. 数据源是否为事件
    ds = args.get("datasource_id")
    if "HISTORY_ADS_EVENT" in ds[1]:
        args["datasource_id"] = ds[1]["HISTORY_ADS_EVENT"]
    else:
        logger.error("数据源不属于广告行为类型")
        exit(-1)
    # Step one: 按数据格式处理
    f = str(args.get("format"))
    if "JSON".__eq__(f):
        ads_import_send(
            AdsEventsJson(
                name=args.get("m"),
                path=args.get("path"),
                debug=args.get("debug"),
                format=f,
                datasourceId=args.get("datasource_id"),
                eventStart=event_start,
                eventEnd=event_end,
                jobName=args.get("jobName"),
                clear=args.get("clear"),
            )
        )
    elif "CSV".__eq__(f):
        separator = args.get("separator")
        separator = "," if separator == "" else separator
        ads_import_send(
            AdsEventsCv(
                name=args.get("m"),
                path=args.get("path"),
                debug=args.get("debug"),
                format=f,
                datasourceId=args.get("datasource_id"),
                attributes=args.get("attributes"),
                separator=separator,
                skipHeader=args.get("skip_header"),
                eventStart=event_start,
                eventEnd=event_end,
                jobName=args.get("jobName"),
                clear=args.get("clear"),
            )
        )
    elif "TSV".__eq__(f):
        separator = args.get("separator")
        separator = "\t" if separator == "" else separator
        ads_import_send(
            AdsEventsCv(
                name=args.get("m"),
                path=args.get("path"),
                debug=args.get("debug"),
                format=f,
                datasourceId=args.get("datasource_id"),
                attributes=args.get("attributes"),
                separator=separator,
                skipHeader=args.get("skip_header"),
                eventStart=event_start,
                eventEnd=event_end,
                jobName=args.get("jobName"),
                clear=args.get("clear"),
            )
        )


# SV格式(CSV、TSV)
def ads_sv_import_prepare_process(
    attributes, paths, skip_header, separator, qualifier, eventStart, eventEnd, debug
):
    """
    1. 校验数据基本信息
    2. SV格式数据转换为数据对象
    """
    # Step 1: 校验有无attributes,有无重复列名
    if attributes is None:
        logger.error("[-attr/--attributes]参数值不存在")
        exit(-1)

    commonlist = ["key", "timestamp", "utm_source", "utm_campaign"]
    ads_attr_keys = [
        "ip",
        "os",
        "osv",
        "platform",
        "ads_id",
        "$ad_group",
        "$ad_plan",
        "$ad_creative",
        "$utm_term",
        "$utm_medium",
        "$utm_content"
    ]
    cols = str(attributes).split(",")
    res = [i for i in cols if i not in commonlist]

    attr_all = BaseConfig.attr_all
    total_error = 0
    for path in paths:
        count = 0
        error = 0
        if skip_header:
            replace_first_line_with_header(path, cols, separator)
        # 读取文件第一行，与预期表头比较
        with open(path, "r", encoding="utf8") as f:
            first_line = f.readline().strip()
            expected_header = separator.join(cols)
            if first_line != expected_header:
                add_header_to_file(path, cols, separator)

        skh = True
        with open(path, "r", encoding="utf8") as f:
            for line in f:
                count += 1
                line = line.replace("\n", "").replace("\\t", "\t")
                # Step 2: 校验数据header列是否一致，数量和顺序
                if skh is True and count == 1:
                    header_normal = True
                    error_key = []
                    for key in res:
                        if key not in ads_attr_keys and key not in attr_all:
                            error_key.append(key)
                    if len(error_key) > 0:
                        logger.error(
                            f"[-attr/--attributes]参数值列:事件属性{error_key}在GIO平台未定义"
                        )
                        header_normal = False
                    if not header_normal:
                        logger.error("header校验失败！")
                        return False
                else:
                    # Step 2: 数据列是否一致
                    line_normal = True
                    if check_sv_header_col_count(cols, line.split(separator)) is False:
                        remove_first_line_from_csv(path)
                        logger.error(
                            f"第{count}行:导入文件[{path}]的列数和参数值列数不一致\n请检查文件分隔符，并通过参数[-sep]指定"
                        )
                        return False
                    if not line_normal:
                        continue
        if debug:
            df = pd.read_csv(
                path,
                sep=separator,
                header=0 if skh else None,
                names=cols if skh else None,
            )
            for index, row in df.iterrows():
                lineNumber = index + 1
                count += 1
                col_value = row.to_dict()
                # 提取必要的字段
                ads_event, error_message = ads_extract_and_validate_data(col_value)
                if ads_event == None:
                    logger.error(
                        f"第{lineNumber}行: 文件[{path}]数据[{row.to_string(index=False)}]:\n{error_message}"
                    )
                    error += 1
                    continue

                # 执行数据对象的校验
                is_valid, error_message = valid_ads_event(
                    ads_event, eventStart, eventEnd
                )
                if not is_valid:
                    logger.error(
                        f"第{lineNumber}行: 文件[{path}]数据[{row.to_string(index=False)}]:\n{error_message}"
                    )
                    error += 1
                    if not skip_header:
                        logger.error("请检查文件表头数据是否新增以参数[attr]参数为准的表头,请根据信息修改文件内容或参数信息")
                    continue
                if count % 500000 == 0:
                    my_logger.info(f"已经校验{count}条数据......")

            if error > 0:
                logger.warn(f"文件[{path}]导入失败，共发现[{error}]个校验错误")
                total_error += error

        if total_error > 0:
            logger.warn(f"总共发现[{total_error}]个校验错误")
            return False
        else:
            return True


def ads_import_send(events):
    """
    ADS行为导入，Json格式数据处理
    """
    # Step 1: 执行Debug
    f = events.format
    if events.debug:
        if "JSON".__eq__(f):
            checkResult = ads_events_debug_process(
                events.path, events.eventStart, events.eventEnd
            )
            if checkResult is not True:
                logger.error("Debug校验未通过")
                exit(-1)
        else:
            checkResult = ads_sv_import_prepare_process(
                attributes=events.attributes,
                paths=events.path,
                skip_header=events.skipHeader,
                separator=events.separator,
                qualifier=events.qualifier,
                eventStart=events.eventStart,
                eventEnd=events.eventEnd,
                debug=events.debug,
            )
            if checkResult is not True:
                logger.error("Debug校验未通过")
                exit(-1)

    if len(str(events.jobName)) == 0 or events.jobName is None:
        jobName = f"Python_ads_events_{time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))}"
    else:
        jobName = events.jobName
    # Step 2: 创建导入任务
    if "JSON".__eq__(f):
        job_info = create_task_json(
            events.eventStart, events.eventEnd, events.datasourceId, jobName
        )
    else:
        job_info = create_task_sv(
            events.eventStart,
            events.eventEnd,
            events.datasourceId,
            jobName,
            events.separator,
        )

    # 任务名重复时，获取不到job信息时，程序直接结束
    if job_info is None:
        logger.error("job_info为空，无法创建导入任务")
        exit(-1)
    else:
        my_logger.info(f"创建导入任务: {job_info}")
    direct = job_info["argument"]["directory"]
    # Step 3: 上传数据到FTP
    my_logger.info(f"文件开始上传至FTP")
    put_file(events.path, direct)

    # Step 4: 启动导入任务
    start_time = time.time()
    trigger_job(job_info["id"])
    my_logger.info(f"开始执行导入任务")
    flag = True
    while flag:
        eventImportJob = getImportJobStatus(job_info["id"])
        if eventImportJob is not None:
            stage = eventImportJob["stage"]
            error = eventImportJob["error"]
            if stage is not None and stage.__eq__("FINISH"):
                end_time = time.time()
                cost_time = end_time - start_time
                my_logger.info("导入成功")
                delete_file(events.path, direct)
                my_logger.info("执行导入任务耗时:%.3f秒" % cost_time)
                flag = False
            elif stage is not None and stage.__eq__("ERROR"):
                if error is not None:
                    message = error.get("message", "No message available")
                else:
                    message = "Error object is None"
                end_time = time.time()
                cost_time = end_time - start_time
                logger.error(f"导入失败,错误信息为[ {message} ] \n FTP文件路径: {direct}")
                my_logger.info("执行导入任务耗时:%.3f秒" % cost_time)
                exit(-1)
        if flag:
            my_logger.info(f"等待任务完成......")
            time.sleep(10)


def create_task_json(start, end, tid, name):
    """
    创建josn任务
    """
    if len(str(name)) == 0:
        body = """{ "operationName":"createEventImportJob", "variables":{ "fileType":"json", "tunnelId":"%s", 
            "timeRange":"abs:%s,%s", "createType":"PYTHON" }, "query":"mutation createEventImportJob($tunnelId: HashId!, 
            $timeRange: String, $fileType: String, $createType: String) { createEventImportJob(tunnelId: $tunnelId, 
            timeRange: $timeRange, fileType: $fileType, createType: $createType) { id name argument { directory 
            __typename } __typename } }" }""" % (
            tid,
            start,
            end,
        )
    else:
        body = """{ "operationName":"createEventImportJob", "variables":{ "fileType":"json", "tunnelId":"%s", 
            "timeRange":"abs:%s,%s", "name":"%s", "createType":"PYTHON" }, "query":"mutation createEventImportJob($name: 
            String, $tunnelId: HashId!, $timeRange: String, $fileType: String, $createType: String) { 
            createEventImportJob(name: $name, tunnelId: $tunnelId, timeRange: $timeRange, fileType: $fileType, 
            createType: $createType) { id name argument { directory __typename } __typename } }" }""" % (
            tid,
            start,
            end,
            name,
        )

    resp = http_util.send_graphql_post(body.encode("utf-8"))
    try:
        return resp["createEventImportJob"]
    except TypeError:
        logger.error("自定义任务名称已存在！")


def create_task_sv(start, end, tid, name, separator):
    """
    创建csv/tsv任务
    """
    separator = separator.replace("\t", "\\\\t")
    if len(str(name)) == 0:
        body = """{ "operationName":"createEventImportJobV2", "variables":{ "fileType":"csv", "tunnelId":"%s", 
            "timeRange":"abs:%s,%s", "createType":"PYTHON", "csvSeparator":"%s" }, "query":"mutation 
            createEventImportJobV2($tunnelId: HashId!, $timeRange: String, $fileType: String, $createType: String, 
            $csvSeparator: String) { createEventImportJobV2(tunnelId: $tunnelId, timeRange: $timeRange, 
            fileType: $fileType, createType: $createType, csvSeparator: $csvSeparator) { id name argument { directory 
            __typename } __typename } }" }""" % (
            tid,
            start,
            end,
            separator,
        )
    else:
        body = """{ "operationName":"createEventImportJobV2", "variables":{ "fileType":"csv", "tunnelId":"%s", 
            "timeRange":"abs:%s,%s", "name":"%s", "createType":"PYTHON", "csvSeparator":"%s" }, "query":"mutation 
            createEventImportJobV2($name: String, $tunnelId: HashId!, $timeRange: String, $fileType: String, 
            $createType: String, $csvSeparator: String) { createEventImportJobV2(name: $name, tunnelId: $tunnelId, 
            timeRange: $timeRange, fileType: $fileType, createType: $createType, csvSeparator: $csvSeparator) { id 
            name argument { directory __typename } __typename } }" }""" % (
            tid,
            start,
            end,
            name,
            separator,
        )

    resp = http_util.send_graphql_post(body.encode("utf-8"))
    try:
        return resp["createEventImportJobV2"]
    except TypeError:
        logger.error("自定义任务名称已存在！")


def ads_events_debug_process(paths, eventStart, eventEnd):
    """
    获客广告数据行为导入Debug
    1、校验文件的数据内容合法性, 是否缺失必要字段(userId,event,timestamp)
    2、校验文件的数据时间范围合法性
    3、校验自定义事件在GIO平台是否定义
    """
    count = 0
    error_count = 0
    correct_count = 0  # 正确行数
    error_dirs = []
    for path in paths:
        my_logger.info(f"start check file: {path}")

        # 1 重命名 文件名 加后缀 _tmp
        names = path.rsplit("/", 1)
        path_tmp = path + "_tmp"
        os.rename(path, path_tmp)  # 如果新文件名的文件 存在 则覆盖 ok的

        names2 = names[0].rsplit("/", 1)
        grandpa_path = names2[0]
        father_path = names2[-1]
        error_file_name = (
            names[-1] + "_" + str(int(round(time.time() * 1000))) + "_error"
        )

        # 错误空文件名
        dir_error = f"{grandpa_path}/{father_path}_error"
        error_dirs.append(dir_error)
        path_error = f"{dir_error}/{error_file_name}"
        if not os.path.exists(dir_error):
            os.makedirs(dir_error)

        # 2 打开 每个文件， 加后缀 _tmp 文件
        with open(path_tmp, "r", encoding="utf8") as f:
            # 打开正确空文件
            with open(path, "w", encoding="utf8") as f_correct:
                # 打开错误空文件
                with open(path_error, "w", encoding="utf8") as f_error:
                    current_file_error_lines = 0
                    for line in f:
                        count = count + 1
                        source_line = (
                            line  # 把原始行数据 保存到 source_line 变量中，后面判断 正常 异常 ，再写入到相应的文件中
                        )
                        line = line.replace("\n", "")
                        if not line == "":
                            try:
                                json_data = json.loads(line.strip())
                            except JSONDecodeError:
                                logger.error(
                                    f"第{count}行:文件[{path}]数据[{line}]:\n数据非JSON格式\n"
                                )
                                error_count += 1
                                current_file_error_lines += 1
                                f_error.write(source_line)  # 写入异常文件
                                continue

                            ads_event, message = ads_extract_and_validate_data(
                                json_data
                            )
                            if ads_event is None:
                                logger.error(
                                    f"第{count}行:文件[{path}]数据[{line}]\n" f"{message}"
                                )
                                error_count += 1
                                current_file_error_lines += 1
                                f_error.write(source_line)  # 写入异常文件
                                continue
                            is_valid, error_message = valid_ads_event(
                                ads_event, eventStart, eventEnd
                            )
                            if not is_valid:  # 异常
                                logger.error(
                                    f"第{count}行:文件[{path}]数据[{line}]:\n"
                                    f"{error_message}"
                                )
                                error_count += 1
                                current_file_error_lines += 1
                                f_error.write(source_line)  # 写入异常文件
                            else:  # 正常
                                f_correct.write(source_line)  # 写入正常文件
                                correct_count = correct_count + 1
                            if count % 500000 == 0:
                                my_logger.info(f"已经校验{count}条数据......")
                        else:
                            logger.warn(f"第{count}行为空，跳过该行")
                f_error.close()  # 关闭 异常文件
            f_correct.close()  # 关闭 正常文件
        f.close()  # 关闭 带有后缀 _tmp的文件

        # 删除 带有后缀 _tmp的文件
        os.remove(path_tmp)
        # 判断 若 异常文件空白 行数=0，则 删除 异常文件
        if current_file_error_lines == 0:
            os.remove(path_error)

    # 判断 若 异常 文件夹 空白，则 删除 该文件夹
    for dir in error_dirs:
        if len(os.listdir(dir)) == 0:
            os.removedirs(dir)

    if error_count == 0:
        my_logger.info(f"本次共校验[{count}]行数据")
    else:
        my_logger.info(
            f"本次共校验[{count}]行数据,其中校验失败[{error_count}]行数据,异常数据已剪切到如下目录中 {error_dirs}"
        )

    if correct_count == 0:
        my_logger.info(f"由于本次正确数据0条，故不生成导数任务。")
        return False
    else:
        return True


def valid_ads_event(adsEvent, eventStart, eventEnd):
    error_message = ""
    try:
        timestamp = time_format(str(adsEvent.timestamp), BaseConfig.timezone)
    except Exception:
        error_message += "timestamp格式错误，请参考数据导入帮助文档\n"
        return False, error_message
    if (timestamp < eventStart or timestamp > eventEnd) and timestamp != 0:
        error_message += "timestamp时间范围不合法\n"
        return False, error_message
    return True, None
    


def ads_extract_and_validate_data(json_data):
    error_message = ""
    columns = ["key", "timestamp", "utm_campaign", "utm_source"]
    for column in columns:
        if column not in json_data:
            error_message += column + "字段不存在\n"

    if error_message != "":
        return None, error_message

    keyValue = json_data.get("key")
    if keyValue not in ["$ads_click", "$ads_imp"]:
        error_message += f"key 必须是 $ads_click 或者 $ads_imp\n"
        return None, error_message

    # 提取字段并创建 AdsEvent 对象
    ads_event = AdsData(
        key=json_data["key"],
        utmSource=json_data["utm_source"],
        utmCampaign=json_data["utm_campaign"],
        timestamp=json_data["timestamp"],
        attrs=json_data.get("attrs", {}),
        dataSourceId=json_data.get("dataSourceId", None),
    )
    return ads_event, error_message
