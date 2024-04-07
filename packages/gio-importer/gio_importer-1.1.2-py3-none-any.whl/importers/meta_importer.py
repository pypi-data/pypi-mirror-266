#!/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright (c) 2020 growingio.com, Inc.  All Rights Reserved
import argparse
import pathlib
import sys

project_root = str(pathlib.Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from importers.common.log_util import my_logger, logger
from importers.meta.meta_create import *


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m',
                        help='必填参数. 创建事件-create_event,创建事件属性-create_event_variables,创建用户属性-create_user_variables,'
                             '创建主体字段-create_item_variables,绑定事件与事件属性-bind_event_variables,导入元数据-export_meta，导出元数据-import_meta',
                        required=True, metavar="")
    parser.add_argument('-ik', '--item_key', help='创建主体时必填参数:指定主体标识符', default="", metavar="")
    parser.add_argument('-k', '--key', help='必填参数. 需要创建事件名', default="", metavar="")
    parser.add_argument('-t', '--type', help='创建事件/用户属性必填参数. 数据类型-(string,int,double)', default="",
                        metavar="")
    parser.add_argument('-a', '--attr', help='绑定事件与属性必填参数，多个属性名使用英文逗号分隔', metavar="")
    parser.add_argument('-n', '--name', help='可选参数. 事件显示名', default="", metavar="")
    parser.add_argument('-d', '--desc', help='可选参数. 事件描述', default="", metavar="")
    parser.add_argument('-f', '--file', help='导入/导出元数据必填参数. 文件名', metavar="")
    parser.add_argument('-analy', '--analysis', help='用于创建分析主体，TRUE-创建分析主体,FALSE-创建主体字典表.',
                        default=False)
    args = parser.parse_args()
    return args.__dict__


def execute_importer(args):
    m = args.get("m")
    analysis = str(args.get('analysis')).upper()
    if 'TRUE'.__eq__(analysis):
        analysis = True
    elif 'FALSE'.__eq__(analysis):
        analysis = False
    else:
        logger.error("[-analy/--analysis]参数值不对")
        exit(-1)
    args['analysis'] = analysis

    if 'create_event'.__eq__(m):
        key = args.get('key')
        check_key(key)
        create_info = create_event(key, args.get('name'), args.get('desc'))
        my_logger.info("创建事件成功", create_info)
    elif 'create_event_variables'.__eq__(m):
        key = args.get('key')
        check_key(key)
        create_info = create_event_variables(key, args.get('type'), args.get('name'), args.get('desc'))
        my_logger.info("创建事件属性成功", create_info)
    elif 'create_user_variables'.__eq__(m):
        key = args.get('key')
        check_key(key)
        create_info = create_user_variables(key, args.get('type'), args.get('name'), args.get('desc'))
        my_logger.info("创建用户属性成功", create_info)
    elif 'create_item'.__eq__(m):
        item_key = args.get('item_key')
        check_key(item_key)
        create_info = create_item(item_key, args['analysis'], args.get('name'), args.get('desc'))
        my_logger.info("创建主体成功", create_info)
    elif 'create_item_variables'.__eq__(m):
        item_key = args.get('item_key')
        check_key(item_key)
        import_item_variables(item_key, args['analysis'], args.get('file'))
    elif 'bind_event_variables'.__eq__(m):
        key = args.get('key')
        check_key(key)
        bind_info, key_list = bind_event_variables(key, args.get('name'), args.get('attr'))
        my_logger.info("成功绑定事件属性:{},info:{}".format(key_list, bind_info))
    elif 'export_meta'.__eq__(m):
        export_meta(args.get('file'))
    elif 'import_meta'.__eq__(m):
        import_meta(args.get('file'))
    else:
        logging.error("请确认填写项目名！")
        exit(-1)


def do_meta(params):
    my_logger.info("Meta Data Task Start")
    # 设置默认参数值
    default_params = {
        'm': '',
        'item_key': '',
        'key': '',
        'type': '',  # 默认为空字符串
        'attr': '',  # 默认为空字符串
        'name': '',  # 默认为空字符串
        'desc': '',  # 默认为空字符串
        'file': '',  # 默认为空字符串
        'analysis': False
    }
    combined_params = {**default_params, **params}

    execute_importer(combined_params)
    my_logger.info("Meta Data Task Finish")


def main():
    args = parse_args()
    execute_importer(args)


if __name__ == '__main__':
    my_logger.info("Meta Data Task Start")
    main()
    my_logger.info("Meta Data Task Finish")
