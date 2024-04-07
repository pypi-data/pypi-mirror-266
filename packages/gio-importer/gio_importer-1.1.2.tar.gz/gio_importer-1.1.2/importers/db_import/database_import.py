import json
import os
import tempfile
import time

from importers.common.common_util import time_str_to_timestamp_of_tz, getItemVariables
from importers.common.config_util import BaseConfig
from importers.common.log_util import logger
from importers.data_import.data_events import ONE_DAY_MILLISECOND, events_import_send
from importers.db_import.hive_import import event_hive_import, user_hive_import, item_hive_import
from importers.db_import.mysql_import import event_mysql_import, user_mysql_import, item_mysql_import
from importers.meta.data_center import getdataCenterItemModels


def events(args):
    try:
        start = time_str_to_timestamp_of_tz(args.get('start_time'), '%Y-%m-%d', BaseConfig.timezone) * 1000
        end = time_str_to_timestamp_of_tz(args.get('end_time'), '%Y-%m-%d',
                                          BaseConfig.timezone) * 1000 + ONE_DAY_MILLISECOND
    except (TypeError, ValueError):
        logger.error("[-s/--start_time]或[-e/--end_time]时间参数格式不对,格式为:YYYY-MM-DD")
        exit(-1)
    ds = args.get('datasource_id')
    if 'HISTORY_EVENT' in ds[1]:
        args['datasource_id'] = ds[1]['HISTORY_EVENT']
    else:
        logger.error("数据源不属于用户行为类型")
        exit(-1)
    f = args.get('format')
    if 'MYSQL'.__eq__(str(f).upper()):
        event_mysql_import(args, start, end)
    elif 'HIVE'.__eq__(str(f).upper()):
        event_hive_import(args, start, end)
    else:
        logger.error("format不在取值范围内")
        exit(-1)


def user_variables(args):
    ds = args.get('datasource_id')
    if 'USER_PROPERTY' in ds[1]:
        args['datasource_id'] = ds[1]['USER_PROPERTY']
    else:
        logger.error("数据源不属于用户属性类型")
        exit(-1)
    if 'MYSQL'.__eq__(str(args.get('format')).upper()):
        user_mysql_import(args)
    elif 'HIVE'.__eq__(str(args.get('format')).upper()):
        user_hive_import(args)
    else:
        logger.error("format不在取值范围内")
        exit(-1)


def item_variables(args):
    keys = getItemVariables(getdataCenterItemModels())
    itemKey = args.get('item_key')
    ds = args.get('datasource_id')
    if 'HISTORY_ITEM' in ds[1]:
        args['datasource_id'] = ds[1]['HISTORY_ITEM']
    else:
        logger.error("数据源不属于主体类型")
        exit(-1)
    if itemKey not in keys:
        logger.error(f"item_Key主体标识符[{itemKey}]不存在")
        exit(-1)

    if 'MYSQL'.__eq__(str(args.get('format')).upper()):
        item_mysql_import(args)
    elif 'HIVE'.__eq__(str(args.get('format')).upper()):
        item_hive_import(args)
    else:
        logger.error("format不在取值范围内")
        exit(-1)
