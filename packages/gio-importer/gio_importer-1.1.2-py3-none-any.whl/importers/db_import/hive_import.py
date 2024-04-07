import json
import os
import time

from pyhive.exc import OperationalError
from importers.common.common_util import get_all_file, remove_file, hive_connect, getVariables
from importers.common.config_util import get_temp_dir_from_config
from importers.common.log_util import logger, my_logger
from importers.data_import.data_events import events_import_send
from importers.data_import.data_format_util import validate_data_event
from importers.data_import.data_item_variable import item_variables_import_send
from importers.data_import.data_model import EventsJson, DataEvent, DataUser, UserVariablesJson, ItemVariablesJson, \
    DataItem
from importers.data_import.data_user_variable import user_variables_import_send
from importers.meta.data_center import getBindEvent, getdataCenterUserVariables, getdataCenterEventVariables


def event_hive_import(args, start, end):
    """
       行为数据导入，HIVE数据源
    """
    try:
        conn = hive_connect(host=args.get('host'),
                            port=int(args.get('port')),
                            user=args.get('user')
                            )
    except TypeError:
        logger.error("HIVE连接失败。")
        exit(-1)
    cursor = conn.cursor()
    try:
        sql = args.get('sql')
        cursor.execute(sql)
        my_logger.info(sql)
    except OperationalError:
        logger.error("请检查SQL语句")
        exit(-1)
    desc = cursor.description
    desc_list = []
    for d in desc:
        desc_list.append(d[0])
    if 'event' not in desc_list or 'timestamp' not in desc_list:
        logger.error("event或timestamp字段不存在")
        exit(-1)
        # 检查userId字段是否存在，如果不存在，则检查userKey字段
    if 'userid' not in desc_list and 'userkey' not in desc_list:
        logger.error("缺少userid需指定\n若传主体事件,则数据需字段userKey,且值为‘$notuser’")
        exit(-1)

    temp_dir = get_temp_dir_from_config()  # 从配置中获取临时存储目录
    current_tmp_path = os.path.join(temp_dir, str(int(round(time.time() * 1000))))
    if os.path.exists(current_tmp_path) is False:
        os.makedirs(current_tmp_path)
    my_logger.info(f"临时存储Json文件目录：[{current_tmp_path}]")
    json_file_abs_path = current_tmp_path + '/' + 'tmp_events.json'
    event = getBindEvent()
    cstm_keys = {}
    for i in event['dataCenterCustomEvents']:
        list = []
        for a in i['attributes']:
            list.append(a['key'])
        cstm_keys[i['key']] = list
    cstm_attr_keys = getVariables(getdataCenterEventVariables())
    try:
        start_time = time.time()
        wf = open(json_file_abs_path, 'w')
        cnt = 0
        count = 0
        while True:
            cnt += 1
            data = cursor.fetchmany(size=args.get('batch'))
            if len(data) == 0 and cnt == 1:
                logger.error("数据为空")
                exit(-1)
            elif len(data) == 0 and cnt > 1:
                end_time = time.time()
                cost_time = end_time - start_time
                my_logger.info("读取SQL数据,写入临时文件耗时:%.3f秒" % cost_time)
                if len(str(args.get('jobName'))) == 0 or args.get('jobName') is None:
                    job_name = f"Python_events_{time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))}"
                else:
                    job_name = args.get('jobName')
                events_import_send(
                    EventsJson(name='events',
                               path=get_all_file(current_tmp_path),
                               format='JSON',
                               debug=False,
                               eventStart=start,
                               eventEnd=end,
                               datasourceId=args.get('datasource_id'),
                               jobName=job_name,
                               clear=False
                               )
                )
                break
            else:
                for row in data:
                    tmp = {}
                    var = {}
                    userId_present = True
                    for a in range(len(row)):
                        if desc_list[a] == 'event' or desc_list[a] == 'timestamp':
                            tmp[desc_list[a]] = row[a]
                        elif desc_list[a] == 'userid':
                            userId_present = False
                            tmp['userId'] = row[a]
                        elif desc_list[a] == 'eventid' and row[a] != '':
                            tmp['eventId'] = row[a]
                        elif desc_list[a] == 'userkey' and row[a] != '':
                            tmp['userKey'] = row[a]
                        else:
                            var[desc_list[a]] = row[a]
                    tmp['attrs'] = var
                    # 检查userId字段，如果不存在则检查userKey是否为$notuser
                    if userId_present:
                        if tmp['userKey'] == '$notuser':
                            tmp['userId'] = ''
                        else:
                            logger.error("导入主体事件时,userKey的值不是$notuser")
                            exit(-1)
                    if 'eventId' in tmp:
                        eventId = tmp['eventId']
                    else:
                        eventId = None
                    if 'userKey' in tmp:
                        userKey = tmp['userKey']
                    else:
                        userKey = ''
                    data_event = DataEvent(userId=tmp['userId'], event=tmp['event'],
                                           timestamp=tmp['timestamp'], attrs=tmp['attrs'],
                                           userKey=userKey, eventId=eventId)
                    is_valid, error_message = validate_data_event(data_event, start, end, cstm_keys,
                                                                  cstm_attr_keys)
                    if not is_valid:  # 异常
                        logger.error(f"{error_message}")
                        exit(-1)
                    wf.write(json.dumps(data_event.__dict__, ensure_ascii=False))
                    wf.write('\n')
                    count += 1
                    if count % 2000000 == 0:
                        my_logger.info(f"已经写入{count}条数据进临时文件......")
                wf.flush()

    finally:
        remove_file(current_tmp_path)


def user_hive_import(args):
    """
       用户属性导入，HIVE数据源
    """
    try:
        conn = hive_connect(host=args.get('host'),
                            port=int(args.get('port')),
                            user=args.get('user'))
    except TypeError:
        logger.error("HIVE连接失败。")
        exit(-1)
    cursor = conn.cursor()
    try:
        sql = args.get('sql')
        cursor.execute(sql)
        my_logger.info(sql)
    except OperationalError:
        logger.error("请检查SQL语句")
        exit(-1)
    desc = cursor.description
    desc_list = []
    for d in desc:
        desc_list.append(d[0])
    if 'userid' not in desc_list:
        logger.error("userId字段不存在")
        exit(-1)

    temp_dir = get_temp_dir_from_config()  # 从配置中获取临时存储目录
    current_tmp_path = os.path.join(temp_dir, str(int(round(time.time() * 1000))))
    if os.path.exists(current_tmp_path) is False:
        os.makedirs(current_tmp_path)
    my_logger.info(f"临时存储Json文件目录：[{current_tmp_path}]")
    keys = getVariables(getdataCenterUserVariables())
    json_file_abs_path = current_tmp_path + '/' + 'tmp_user.json'
    start_time = time.time()
    try:
        wf = open(json_file_abs_path, 'w')
        cnt = 0
        count = 0
        while True:
            cnt += 1
            data = cursor.fetchmany(size=args.get('batch'))
            if len(data) == 0 and cnt == 1:
                logger.error("数据为空")
                exit(-1)
            elif len(data) == 0 and cnt > 1:
                end_time = time.time()
                cost_time = end_time - start_time
                my_logger.info("读取SQL数据,写入临时文件耗时:%.3f秒" % cost_time)
                if len(str(args.get('jobName'))) == 0 or args.get('jobName') is None:
                    job_name = f"Python_user_{time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))}"
                else:
                    job_name = args.get('jobName')
                user_variables_import_send(
                    UserVariablesJson(name='user_variables',
                                      path=get_all_file(current_tmp_path),
                                      debug=False,
                                      format='JSON',
                                      datasourceId=args.get('datasource_id'),
                                      jobName=job_name,
                                      clear=False)
                )
                break
            else:
                json_list = []
                for row in data:
                    res = {}
                    var = {}
                    for a in range(len(row)):
                        if desc_list[a] == 'userid':
                            res['userId'] = row[a]
                        elif desc_list[a] == 'userkey' and row[a] != '':
                            res['userKey'] = row[a]
                        else:
                            var[desc_list[a]] = row[a]
                    res['attrs'] = var
                    json_list.append(res)
                for json_str in json_list:
                    for key in json_str['attrs']:
                        if key not in keys and key.startswith("$") is False:
                            logger.error("用户属性{}在GIO平台未定义".format(key))
                            exit(-1)
                    if 'userKey' in json_str:
                        userKey = json_str['userKey']
                        if userKey == '$notuser':
                            logger.error("用户属性导入不支持用户身份为‘$notuser’")
                            exit(-1)
                    else:
                        userKey = ''
                    data_event = DataUser(userId=json_str['userId'], userKey=userKey, attrs=json_str['attrs'])
                    wf.write(json.dumps(data_event.__dict__, ensure_ascii=False))
                    wf.write('\n')
                    count += 1
                    if count % 2000000 == 0:
                        my_logger.info(f"已经写入{count}条数据进临时文件......")
                wf.flush()
    finally:
        remove_file(current_tmp_path)


def item_hive_import(args):
    """
       主体导入，HIVE数据源
    """
    try:
        conn = hive_connect(host=args.get('host'),
                            port=int(args.get('port')),
                            user=args.get('user'))
    except TypeError:
        logger.error("HIVE连接失败。")
        exit(-1)
    cursor = conn.cursor()
    try:
        sql = args.get('sql')
        cursor.execute(sql)
        my_logger.info(sql)
    except OperationalError:
        logger.error("请检查SQL语句")
        exit(-1)
    desc = cursor.description
    desc_list = []
    for d in desc:
        desc_list.append(d[0])
    if 'item_id' not in desc_list:
        logger.error("item_id字段不存在")
        exit(-1)

    temp_dir = get_temp_dir_from_config()  # 从配置中获取临时存储目录
    current_tmp_path = os.path.join(temp_dir, str(int(round(time.time() * 1000))))
    if os.path.exists(current_tmp_path) is False:
        os.makedirs(current_tmp_path)
    my_logger.info(f"临时存储Json文件目录：[{current_tmp_path}]")
    json_file_abs_path = current_tmp_path + '/' + args.get('item_key') + '.json'
    start_time = time.time()
    try:
        wf = open(json_file_abs_path, 'w')
        cnt = 0
        count = 0
        while True:
            cnt += 1
            data = cursor.fetchmany(size=args.get('batch'))
            if len(data) == 0 and cnt == 1:
                logger.error("数据为空")
                exit(-1)
            elif len(data) == 0 and cnt > 1:
                my_logger.info(f"临时文件总共写入{count}条数据")
                end_time = time.time()
                cost_time = end_time - start_time
                my_logger.info("读取SQL数据,写入临时文件耗时:%.3f秒" % cost_time)
                if len(str(args.get('jobName'))) == 0 or args.get('jobName') is None:
                    job_name = f"Python_item_{time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))}"
                else:
                    job_name = args.get('jobName')
                item_variables_import_send(
                    ItemVariablesJson(name='item_variables',
                                      path=get_all_file(current_tmp_path),
                                      debug=True,
                                      format='JSON',
                                      datasourceId=args.get('datasource_id'),
                                      itemKey=args.get('item_key'),
                                      jobName=job_name,
                                      clear=False)
                )
                break
            else:
                json_list = []
                for row in data:
                    res = {}
                    var = {}
                    for a in range(len(row)):
                        if desc_list[a] == 'item_id' and row[a] != '':
                            res['item_id'] = row[a]
                        else:
                            var[desc_list[a]] = row[a]
                    res['attrs'] = var
                    json_list.append(res)
                for json_str in json_list:
                    data_item = DataItem(item_id=json_str['item_id'], attrs=json_str['attrs'])
                    wf.write(json.dumps(data_item.__dict__, ensure_ascii=False))
                    wf.write('\n')
                    count += 1
                    if count % 2000000 == 0:
                        my_logger.info(f"已经写入{count}条数据进临时文件......")
                wf.flush()
    finally:
        remove_file(current_tmp_path)
