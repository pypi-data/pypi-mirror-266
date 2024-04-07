#!/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright (c) 2020 growingio.com, Inc.  All Rights Reserved
import argparse
import os
import pathlib
import sys

sys.path.append(str(pathlib.Path(os.path.abspath(__file__)).parent.parent))
from importers.meta.meta_create import *
from importers.clear_data.clear_data import globalMetricJob


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m',
                        help='必填参数. 触发任务名',
                        required=True, metavar="")
    parser.add_argument('-s', '--start_time',
                        help='可选参数. 数据起始时间,导入用户行为数据时指定',
                        default='',
                        type=str)
    parser.add_argument('-e', '--end_time',
                        help='可选参数. 数据结束时间,导入用户行为数据时指定',
                        default='',
                        type=str)
    args = parser.parse_args()
    return args.__dict__


def main():
    args = parse_args()
    m = args.get("m")
    if 'GlobalMetricDailyPipeline'.__eq__(m):
        globalMetricJob(args.get("start_time"), args.get("end_time"))
    else:
        logging.error("请确认填写项目名！")
        exit(-1)


if __name__ == '__main__':
    main()
