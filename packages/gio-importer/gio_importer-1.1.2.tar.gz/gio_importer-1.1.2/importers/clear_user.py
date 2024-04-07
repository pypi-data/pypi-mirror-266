#!/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright (c) 2020 growingio.com, Inc.  All Rights Reserved
import argparse
import pathlib
import sys

project_root = str(pathlib.Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from importers.common.log_util import my_logger
from importers.meta.meta_create import *
from importers.clear_data.clear_data import clearUserData, clearUserMeta


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m',
                        help='必填参数. 触发用户删除任务-clear_users，批量添加待删除用户-clear_users_meta',
                        required=True, metavar="")
    parser.add_argument('-n', '--now',
                        help='可选参数. True-立即执行离线任务,false-天任务执行清理任务')
    parser.add_argument('-u', '--users',
                        help='可选参数, 添加待删除用户', type=str)
    args = parser.parse_args()
    return args.__dict__


def execute_importer(args):
    m = args.get("m")
    if 'clear_users'.__eq__(m):
        clearUserData(args.get("now"))
    elif 'clear_users_meta'.__eq__(m):
        clearUserMeta(args.get("users"))
    else:
        logging.error("请确认填写项目名！")
        exit(-1)



def do_user(params):
    my_logger.info("Clear User Task Start")
    execute_importer(params)
    my_logger.info("Clear User Task Finish")

def main():
    args = parse_args()
    execute_importer(args)


if __name__ == '__main__':
    my_logger.info("Clear User Task Start")
    main()
    my_logger.info("Clear User Task Finish")
