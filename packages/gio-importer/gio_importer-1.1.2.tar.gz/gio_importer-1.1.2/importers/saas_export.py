#!/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright (c) 2020 growingio.com, Inc.  All Rights Reserved
import argparse
import os
import pathlib
import sys
import logging

sys.path.append(str(pathlib.Path(os.path.abspath(__file__)).parent.parent))
from importers.saas_export.saas_meta import getSaasMeta


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m',
                        help='必填参数. 创建事件-create_event,创建事件属性-create_event_variables,创建用户属性-create_user_variables,绑定事件与事件属性-bind_event_variables,导入元数据-export_meta，导出元数据-import_meta',
                        required=True, metavar="")
    parser.add_argument('-f', '--file', help='导入/导出元数据必填参数. 文件名', metavar="")
    args = parser.parse_args()
    return args.__dict__


def main():
    args = parse_args()
    m = args.get("m")
    if 'export_saas_meta'.__eq__(m):
        getSaasMeta(args.get("file"))
    else:
        logging.error("请确认填写项目名！")
        exit(-1)


if __name__ == '__main__':
    main()
