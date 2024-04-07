import csv
import json
import os

import pandas as pd

from importers.common import http_util
from importers.common.config_util import ApiConfig, get_temp_dir_from_config
from importers.data_import.data_model import ItemVariablesJson, ItemVariablesSv
from importers.data_import.data_format_util import *
from importers.common.log_util import logger, my_logger
from importers.meta.check_util import check_item_var_key_data_exsit, check_item_var_exsit
from importers.meta.data_center import trigger_job, getImportJobStatus


def item_variables_import(args):
    """
     主体导入，按数据格式处理
    """
    ds = args.get('datasource_id')
    if 'HISTORY_ITEM' in ds[1]:
        args['datasource_id'] = ds[1]['HISTORY_ITEM']
    else:
        logger.error("数据源不属于主体数据类型")
        exit(-1)
    # Step one: 按数据格式处理
    f = str(args.get('format'))
    if 'JSON'.__eq__(f):
        item_variables_import_send(
            ItemVariablesJson(name=args.get('m'), path=args.get('path'), debug=args.get('debug'), format=f,
                              datasourceId=args.get('datasource_id'), itemKey=args.get('item_key'),
                              jobName=args.get('jobName'),
                              clear=args.get('clear'))
        )
    elif 'CSV'.__eq__(f):
        separator = args.get("separator")
        separator = ',' if separator == '' else separator
        item_variables_import_send(
            ItemVariablesSv(name=args.get('m'), path=args.get('path'), debug=args.get('debug'), format=f,
                            datasourceId=args.get('datasource_id'), itemKey=args.get('item_key'),
                            jobName=args.get('jobName'),
                            attributes=args.get('attributes'), separator=separator, skipHeader=args.get('skip_header'),
                            clear=args.get('clear'))
        )
    elif 'TSV'.__eq__(f):
        separator = args.get("separator")
        separator = '\t' if separator == '' else separator
        item_variables_import_send(
            ItemVariablesSv(name=args.get('m'), path=args.get('path'), debug=args.get('debug'), format=f,
                            datasourceId=args.get('datasource_id'), itemKey=args.get('item_key'),
                            jobName=args.get('jobName'),
                            attributes=args.get('attributes'), separator=separator, skipHeader=args.get('skip_header'),
                            clear=args.get('clear'))
        )


def sv_import_prepare_process(attributes, paths, skip_header, separator, qualifier, itemKey):
    """
      1.校验数据基本信息
      2.CSV/TSV格式数据处理
    """
    # Step 1: 校验有无attributes,有无重复列名
    if attributes is None:
        logger.error(f"[-attr/--attributes]参数值不存在")
        exit(-1)

    cols = str(attributes).split(',')
    duplicate_col = check_sv_col_duplicate(cols)
    flag, var_id, var_name, var_desc = check_item_var_exsit(itemKey)
    if flag:
        keys = check_item_var_key_data_exsit(var_id)
    else:
        logger.error(f"item_Key主体标识符[{itemKey}]不存在，校验终止")
        exit(-1)

    if duplicate_col is not None:
        logger.error(f"[-attr/--attributes]出现重复列值[{duplicate_col}]")
        exit(-1)
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
        df = pd.read_csv(path, sep=separator, header=0 if skip_header else None,
                         names=cols if not skip_header else None)
        # Step 2 & 3: 校验数据列是否一致
        for index, row in df.iterrows():
            if len(row) != len(cols):
                remove_first_line_from_csv(path)
                logger.error(
                    f"文件[{path}]的第{index + 1}行数据列数与文件头部列数不一致\n请检查文件分隔符，并通过参数[-sep]指定")
                exit(-1)

            col_value = row.to_dict()
            attrs = {key: value for key, value in col_value.items() if
                     len(str(value)) != 0 and key != 'item_id' and not key.startswith('$')}

            # 确保 attrs 中的所有键都在 keys 中
            if not all(key in keys for key in attrs):
                invalid_keys = [key for key in attrs if key not in keys]
                logger.error(f"以下列名主体字段中不存在: {invalid_keys}")
                exit(-1)
    my_logger.info(f"本次共校验[{count}]行数据")
    return True


def item_variables_import_send(itemVariables):
    """
       主体，Json格式数据处理
    """
    itemKey = itemVariables.itemKey
    f = itemVariables.format
    # Step 1: 执行Debug
    if itemVariables.debug:
        if 'JSON'.__eq__(f):
            if json_variables_debug_process(itemVariables.path, itemKey) is not True:
                logger.error("Debug校验未通过")
                exit(-1)
        else:
            if sv_import_prepare_process(attributes=itemVariables.attributes,
                                         paths=itemVariables.path,
                                         skip_header=itemVariables.skipHeader,
                                         separator=itemVariables.separator,
                                         qualifier=itemVariables.qualifier,
                                         itemKey=itemKey) is not True:
                logger.error("Debug校验未通过")
                exit(-1)
    else:
        lines_count = count_lines_in_file(itemVariables.path)
        my_logger.info(f"本次共导入[{lines_count}]行数据")

    if len(str(itemVariables.jobName)) == 0 or itemVariables.jobName is None:
        jobName = f"Python_item_{time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))}"
    else:
        jobName = itemVariables.jobName

    # Step 2: 创建导入任务
    if 'JSON'.__eq__(f):
        job_info = create_task_json(itemVariables.datasourceId, jobName, itemKey)
    else:
        job_info = create_task_sv(itemVariables.datasourceId, jobName, itemKey, itemVariables.separator)

    # 任务名重复时，获取不到job信息时，程序直接结束
    if job_info is None:
        logger.error("job_info为空，无法创建导入任务")
        exit(-1)
    else:
        my_logger.info(f"创建导入任务: {job_info}")
    direct = job_info['argument']['directory']
    # Step 3: 上传数据到FTP
    my_logger.info(f"文件开始上传至FTP")
    put_file(itemVariables.path, direct)

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
                delete_file(itemVariables.path, direct)
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


def create_task_json(ds, name, itemKey):
    """
           创建任务,允许用户自定义更改任务名称
        """
    if len(str(name)) == 0:
        body = '''{ "operationName": "createEventImportJob", "variables": { "fileType":"ftp", "timeRange":"", 
        "tunnelId": "%s", "itemModel":{ "key": "%s" }, "createType":"PYTHON" }, "query": "mutation 
        createEventImportJob($tunnelId: HashId!, $timeRange: String, $fileType: String, $itemModel: ItemModelIdInput, 
        $createType: String) { createEventImportJob(tunnelId: $tunnelId, timeRange: $timeRange,fileType: $fileType, 
        itemModel:$itemModel, createType: $createType) { id name argument { directory __typename } __typename } }" 
        }''' % (ds, itemKey)
    else:
        body = '''{ "operationName":"createEventImportJob", "variables":{ "fileType":"ftp", "tunnelId":"%s", 
            "timeRange":"", "name":"%s", "itemModel":{ "key": "%s" }, "createType":"PYTHON" }, "query":"mutation 
            createEventImportJob($name: String, $tunnelId: HashId!, $timeRange: String, $fileType: String, $itemModel: 
            ItemModelIdInput, $createType: String) { createEventImportJob(name: $name, tunnelId: $tunnelId, timeRange: 
            $timeRange, fileType: $fileType, itemModel:$itemModel, createType: $createType) { id name argument { 
            directory __typename } __typename } }" }''' % (ds, name, itemKey)
    resp = http_util.send_graphql_post(body.encode('utf-8'))
    try:
        return resp['createEventImportJob']
    except TypeError:
        logger.error("自定义任务名称已存在！")


def create_task_sv(ds, name, itemKey, separator):
    """
           创建任务,允许用户自定义更改任务名称
        """
    separator = separator.replace("\t", "\\\\t")
    if len(str(name)) == 0:
        body = '''{ "operationName": "createEventImportJobV2", "variables": { "fileType":"csv", "timeRange":"", 
        "tunnelId": "%s", "itemModel":{ "key": "%s" }, "createType":"PYTHON", "csvSeparator":"%s" }, 
        "query": "mutation createEventImportJobV2($tunnelId: HashId!, $timeRange: String, $fileType: String, 
        $itemModel: ItemModelIdInput, $createType: String, $csvSeparator: String) { createEventImportJobV2(tunnelId: 
        $tunnelId, timeRange: $timeRange,fileType: $fileType, itemModel:$itemModel, createType: $createType, 
        csvSeparator: $csvSeparator) { id name argument { directory __typename } __typename } }" }''' % (
            ds, itemKey, separator)
    else:
        body = '''{ "operationName":"createEventImportJobV2", "variables":{ "fileType":"csv", "tunnelId":"%s", 
        "timeRange":"", "name":"%s", "itemModel":{ "key": "%s" }, "createType":"PYTHON", "csvSeparator":"%s" }, 
        "query":"mutation createEventImportJobV2($name: String, $tunnelId: HashId!, $timeRange: String, $fileType: 
        String, $itemModel: ItemModelIdInput, $createType: String, $csvSeparator: String) { createEventImportJobV2(
        name: $name, tunnelId: $tunnelId, timeRange: $timeRange, fileType: $fileType, itemModel:$itemModel, 
        createType: $createType, csvSeparator: $csvSeparator) { id name argument { directory __typename } __typename 
        } }" }''' % (ds, name, itemKey, separator)
    resp = http_util.send_graphql_post(body.encode('utf-8'))
    try:
        return resp['createEventImportJobV2']
    except TypeError:
        logger.error("自定义任务名称已存在！")


def json_variables_debug_process(paths, itemKey):
    """
    主体导入Debug
    1、校验有无itemKey
    2、校验主体(条件:是否是平台内置和是否定义)
    """
    count = 0
    dict_count = 0
    error_count = 0
    correct_count = 0  # 正确行数
    error_dict = {}
    flag, var_id, var_name, var_desc = check_item_var_exsit(itemKey)
    if flag:
        key_list = check_item_var_key_data_exsit(var_id)
    else:
        logger.error(f"item_Key主体标识符[{itemKey}]不存在，校验终止")
        return False  # 直接退出校验并返回 False
    temp_dir = get_temp_dir_from_config()  # 从配置中获取临时存储目录
    current_tmp_name = str(int(round(time.time() * 1000))) + "_error"
    current_tmp_path = os.path.join(temp_dir, current_tmp_name)
    if not os.path.exists(current_tmp_path):
        os.makedirs(current_tmp_path)
    for path in paths:
        # Define error file path
        error_file_name = 'item_' + str(int(round(time.time() * 1000))) + '_error.json'
        error_path = current_tmp_path + '/' + error_file_name

        with open(path, 'r', encoding='utf8') as f:
            with open(error_path, 'w', encoding='utf8') as f_error:
                lines_to_write = []  # Collect lines to write back to original file
                for line in f:
                    count = count + 1
                    line = line.replace('\n', '')
                    if not line == '':
                        normal = True
                        error_message = ""
                        try:
                            data_dictionary = json.loads(line)
                            # item_id
                            if 'item_id' not in data_dictionary:
                                normal = False
                                error_message += f"item_id不存在\n"
                            # 主体
                            if 'attrs' in data_dictionary:
                                if not isinstance(data_dictionary['attrs'], dict):
                                    normal = False
                                    error_message += f"attrs数据格式不对\n"
                                for key in data_dictionary['attrs']:
                                    if key not in key_list:
                                        normal = False
                                        error_message += f"主体字段[{key}]不存在\n"
                                    elif data_dictionary['attrs'][key] is None or data_dictionary['attrs'][key] == "":
                                        print(
                                            f"主体[{data_dictionary['item_id']}]中字段[{key}]的值为空或为NULL,请检查原始数据\n")
                        except json.JSONDecodeError:
                            normal = False
                            error_message += f"文件[{path}]数据[{line}]非JSON格式\n"

                        if not normal:  # 异常
                            error_hash = hash(error_message)
                            if error_hash not in error_dict:
                                error_dict[error_hash] = error_message
                                logger.error(f"第{count}行:文件[{path}]数据[{line}],\n"
                                             f"{error_message}")
                                dict_count += 1
                            error_count += 1
                            f_error.write(line + '\n')  # 写入异常数据到错误文件
                        else:  # 正常
                            lines_to_write.append(line)  # 添加到待写入的行列表
                            correct_count = correct_count + 1
                        if count % 500000 == 0:
                            my_logger.info(f"已经校验{count}条数据......")

                        if dict_count >= 10000:
                            logger.error("数据内容错误条数已经超过 10000 条, 请先修正数据 ")
                            exit(-1)
                    else:
                        logger.warn(f"第{count}行为空，跳过该行")

                # Write valid lines back to the original file
                with open(path, 'w', encoding='utf8') as f_original:
                    for line in lines_to_write:
                        f_original.write(line + '\n')

        f_error.close()  # 关闭错误文件
        f.close()  # 关闭原始文件
        # 判断 若 异常文件空白 行数=0，则 删除 异常文件
        if error_count == 0:
            os.remove(error_path)
    if len(os.listdir(current_tmp_path)) == 0:
        os.removedirs(current_tmp_path)

    if error_count == 0:
        my_logger.info(f"本次共校验[{count}]行数据")
    else:
        my_logger.info(
            f"本次共校验[{count}]行数据,其中校验失败[{error_count}]行数据,包含[{dict_count}]种错误类型，具体错误内容看上方日志详情,异常数据已剪切到临时文件目录[{current_tmp_path}]")

    if correct_count == 0:
        my_logger.info(f"由于本次正确数据0条，故不生成导数任务。")
        return False
    else:
        return True
