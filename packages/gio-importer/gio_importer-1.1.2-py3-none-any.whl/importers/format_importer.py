#!/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright (c) 2020 growingio.com, Inc.  All Rights Reserved
import argparse
import pathlib
import sys

project_root = str(pathlib.Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from importers.db_import.database_import import events, user_variables, item_variables
from importers.common.log_util import logger, my_logger
from importers.meta.meta_create import *


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m',
                        help='必填参数. 事件events，用户属性user_variables，主体数据导入item_variables.',
                        required=True,
                        type=str)
    parser.add_argument('-ds', '--datasource_id',
                        help='必填参数. 数据源ID.',
                        required=True,
                        type=str)
    parser.add_argument('-item_key',
                        help='必填参数. item_key',
                        required=False,  # 根据-m参数判断是否必填
                        default='',
                        type=str)
    parser.add_argument('-f', '--format',
                        help='可选参数. 导入数据格式,目前支持mysql、hive格式.',
                        type=str,
                        metavar="")
    parser.add_argument('-db_host', '--host',
                        help='必填参数. 客户数据源地址',
                        metavar="")
    parser.add_argument('-db_user', '--user',
                        help='必填参数. 客户数据源用户',
                        type=str,
                        metavar="")
    parser.add_argument('-db_pass', '--password',
                        help='必填参数. 客户数据源密码',
                        type=str,
                        metavar="")
    parser.add_argument('-db_port', '--port',
                        help='必填参数. 客户数据源端口',
                        metavar="")
    parser.add_argument('-sql', '--sql',
                        help='必选参数. sql语句',
                        type=str,
                        metavar="")
    parser.add_argument('-b', '--batch',
                        help='可选参数. hive模式下每批次处理多少条数据',
                        type=int,
                        default=100000,
                        metavar="")
    parser.add_argument('-s', '--start_time',
                        help='用户行为数据必选参数. 开始时间',
                        metavar="")
    parser.add_argument('-e', '--end_time',
                        help='用户行为数据必选参数. 结束时间',
                        metavar="")
    parser.add_argument('-j', '--jobName',
                        help='指定导入任务名称',
                        metavar="")
    parser.add_argument('-c', '--clear',
                        help='可选参数. True-导入数据成功后清理掉FTP上数据,False-导入数据成功后不清理掉FTP上数据.',
                        default=False)
    args = parser.parse_args()
    return args.__dict__


def execute_importer(args):
    tunnels = getTunnels()
    m = args.get('m')
    if args.get('datasource_id') not in tunnels:
        logger.error("数据源不存在")
        exit(-1)
    args['datasource_id'] = [args.get('datasource_id'), tunnels[args.get('datasource_id')]]
    if 'events'.__eq__(m):
        events(args)
    elif 'user_variables'.__eq__(m):
        user_variables(args)
    elif 'item_variables'.__eq__(m):
        item_variables(args)
    else:
        logging.error("请确认填写项目名！")
        exit(-1)


def do_importer(params):
    my_logger.info("Data Importer Start")
    # 设置默认参数值
    default_params = {
        'm': None,  # 必填参数, 没有默认值
        'datasource_id': None,  # 必填参数, 没有默认值
        'item_key': '',  # 默认为空字符串
        'format': None,  # 可选参数, 没有默认值
        'host': None,  # 必填参数, 没有默认值
        'user': None,  # 必填参数, 没有默认值
        'password': None,  # 必填参数, 没有默认值
        'port': None,  # 必填参数, 没有默认值
        'sql': None,  # 必选参数, 没有默认值
        'batch': 100000,  # 默认为 100000
        'start_time': None,  # 用户行为数据必选参数, 没有默认值
        'end_time': None,  # 用户行为数据必选参数, 没有默认值
        'jobName': None,  # 可选参数, 没有默认值
        'clear': False,  # 默认为 False
    }

    combined_params = {**default_params, **params}
    # 如果 params 中有相同的键，则 params 的值会覆盖 default_params 中的默认值
    execute_importer(combined_params)
    my_logger.info("Data Importer Finish")


def main():
    args = parse_args()
    execute_importer(args)


if __name__ == '__main__':
    my_logger.info("Data Importer Start")
    main()
    my_logger.info("Data Importer Finish")
