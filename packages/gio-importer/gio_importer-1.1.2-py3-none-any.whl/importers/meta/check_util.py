import logging

from importers.meta.data_center import *
import re


def check_key(key):
    """
     校验标识符KEY，不能为空，长度小于100，只可以由字母数字下划线组成，且只能字母开头
    :param key: 字符串
    :return:
    """
    if key == '':
        logging.error("事件名不能为空")
        exit(-1)
    elif len(key) > 100:
        logging.error("事件名<{}>长度超限".format(key))
        exit(-1)
    elif key[0].isdigit() or is_chinese(key) or match(key):
        logging.error("事件名<{}>不合法，只可以由字母数字下划线组成，且只能字母开头~".format(key))
        exit(-1)


def check_name(name, key):
    """
     校验name，长度小于100，当name为空，则默认与标识符一致
    :param name: 名称
    :param key: 标识符
    :return:
    """
    if name != "" and len(name) > 100:
        logging.error("显示名<{}>长度超限~".format(name))
        exit(-1)
    elif len(str(name).strip()) == 0:
        return key
    # elif isexsit_eventvar(name) or isexsit_usertvar(name):
    #     logging.error("名称<{}>已重复~".format(name))
    #     exit(-1)
    else:
        return name


def check_desc(desc):
    """
     校验desc，长度小于150，当name为空，则默认与标识符一致
    :param desc: 描述
    :return:
    """
    if desc != "" and len(desc) > 150:
        logging.error("描述<{}>长度超限~".format(desc))
        exit(-1)
    else:
        return desc


def isexsit_eventvar(name):
    """
     校验事件属性名称是否存在
     :param name: 名称
     :return: True/False
     """
    event_variables = getdataCenterEventVariables()
    for var in event_variables:
        if var['name'] == name:
            return True
    return False


def isexsit_usertvar(name):
    """
     校验用户属性名称是否存在
     :param name: 名称
     :return: True/False
     """
    user_variables = getdataCenterUserVariables()
    for var in user_variables:
        if var['name'] == name:
            return True
    return False


def check_event_valuetype(tp):
    """
     校验事件数据类型
     :param tp: 数据类型
     :return:
     """
    if tp == '':
        logging.error("数据类型<{}>未设置".format(tp))
        exit(-1)
    elif tp not in ('string', 'int', 'double'):
        logging.error("数据类型<{}>不在可选值范围".format(tp))
        exit(-1)


def check_user_valuetype(tp):
    """
     校验用户数据类型
     :param tp: 数据类型
     :return:
     """
    if tp == '':
        logging.error("数据类型<{}>未设置".format(tp))
        exit(-1)
    elif tp not in ('string', 'int', 'date', 'double'):
        logging.error("数据类型<{}>不在可选值范围".format(tp))
        exit(-1)


def check_item_key(key):
    """
     校验主体标识符KEY，不能为空，长度小于100，只可以由字母数字下划线组成，且只能字母开头
    :param key: 字符串
    :return:
    """
    if key == '':
        logging.error("主体标识符不能为空")
        exit(-1)
    elif len(key) > 100:
        logging.error("主体标识符<{}>长度超限".format(key))
        exit(-1)
    elif key[0].isdigit() or is_chinese(key) or match(key):
        logging.error("主体标识符<{}>不合法，只可以由字母数字下划线组成，且只能字母开头~".format(key))
        exit(-1)


def check_item_key_variables(key):
    """
     校验主体标识符KEY，不能为空，长度小于100，只可以由字母数字下划线组成，且只能字母开头
    :param key: 字符串
    :return:
    """
    if key == '':
        logging.error("主体字段不能为空")
        exit(-1)
    elif len(key) > 100:
        logging.error("主体字段<{}>长度超限".format(key))
        exit(-1)
    elif key[0].isdigit() or is_chinese(key) or match(key):
        logging.error("主体字段<{}>不合法，只可以由字母数字下划线组成，且只能字母开头~".format(key))
        exit(-1)


def check_item_valuetype(tp):
    """
     校验主体数据类型
     :param tp: 数据类型
     :return:
     """
    if tp == '':
        logging.error("数据类型<{}>未设置".format(tp))
        exit(-1)
    elif tp not in ('string', 'list', 'int', 'date', 'double'):
        logging.error("数据类型<{}>不在可选值范围".format(tp))
        exit(-1)


def check_event_exsit(key):
    """
     校验事件标识符KEY是否存在
     :param key: 标识符
     :return:
     """
    custom_events = getdataCenterCustomEvents()
    for var in custom_events:
        if var['key'] == key:
            return True, var
    else:
        return False, ''


def check_event_attr_exsit(key):
    """
     校验事件标识符KEY是否存在
     :param key: 标识符
     :return:
     """
    custom_events = getdataCenterCustomEventsAndAttr()
    id_list = []
    for var in custom_events:
        if var['key'] == key:
            if len(var['attributes']) != 0:
                for a in var['attributes']:
                    id_list.append(a['id'])
                return True, var, id_list
            else:
                return True, var, id_list
    else:
        return False, '', []


def check_event_var_exsit(key):
    """
     校验事件属性标识符KEY是否存在
     :param key: 标识符
     :return:
     """
    event_variables = getdataCenterEventVariables()
    for var in event_variables:
        if var['key'] == key:
            return True, var
    else:
        return False, ''


def check_user_var_exsit(key):
    """
     校验用户属性标识符KEY是否存在
     :param key: 标识符
     :return:
     """
    user_variables = getdataCenterUserVariables()
    for var in user_variables:
        if var['key'] == key:
            return True, var
    else:
        return False, ''


def check_item_var_exsit(key):
    """
     校验主体标识符KEY是否存在
     :param key: 标识符
     :return:
     """
    item_variables = getdataCenterItemModels()
    for item in item_variables:
        for attr in item['attributes']:
            if attr['isPrimaryKey'] and attr['key'] == key:
                return True, item['id'], item['name'], item['description']

    return False, '', '', ''


def check_item_key_exsit(key):
    """
     校验新主体字段标识符KEY是否存在
     :param key: 标识符
     :return:
     """
    item_variables = getdataCenterItemModels()
    for item in item_variables:
        for attr in item['attributes']:
            if attr['key'] == key:
                logging.error("字段标识符<{}>全局有重复".format(key))
                exit(-1)


def check_item_name_exsit(name):
    """
     校验新主体名称name是否存在
     :param key: 标识符
     :return:
     """
    item_variables = getdataCenterItemModels()
    for item in item_variables:
        for attr in item['attributes']:
            if attr['name'] == name and name != "":
                logging.error("名称<{}>全局有重复".format(name))
                exit(-1)


def check_item_var_key_exsit(id, key):
    """
     校验主体字段KEY是否存在
     :param key: 标识符
     :return:
     """
    item_variables = getdataCenterItemModels()
    for item in item_variables:
        for attr in item['attributes']:
            if item['id'] == id and attr['isPrimaryKey'] is False and attr['key'] == key:
                return True, attr['name'], attr['valueType'], attr['description'], attr['id']

    return False, '', '', '', ''


def check_item_var_key_data_exsit(old_id):
    """
     校验主体字段KEY是否存在
     :param key: 标识符
     :return:
     """
    item_variables = getdataCenterItemModels()
    key_list = []
    for item in item_variables:
        for attr in item['attributes']:
            if item['id'] == old_id and attr['isPrimaryKey'] is False:
                key_list.append(attr['key'])
    return key_list



def check_bind_event_exsit(key):
    """
     校验事件与事件属性
     :param key: 标识符
     :return:
     """
    custom_events = getdataCenterCustomEvents()
    for var in custom_events:
        if var['key'] == key:
            return True, var['id'], var['description']
    else:
        return False, '', ''


def check_key_name(var_list, key, name):
    """
     校验标识符、名称
     :param var_list: 变量列表
     :param key: 标识符
     :param name: 名称
     :return:
     """
    for var in var_list:
        if var['key'] == key:
            logging.error("标识符<{}>已存在~".format(key))
            exit(-1)
        elif var['name'] == name:
            logging.error("名称<{}>已存在~".format(name))
            exit(-1)


def is_chinese(string):
    """
     检测字符串是否存在汉字
     :param string: 字符串
     :return:True/False
     """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def match(str):
    """
     只可以由字母数字下划线组成，且只能字母开头
     :param str: 字符串
     :return:True/False
     """
    mh = re.match(r'[0-9a-zA-Z_]*', str)
    if len(mh.group()) != len(str):
        return True
    else:
        return False


def check_attr(attr):
    """
     校验事件与事件属性
     :param attr: 事件属性
     :return:id_list,key_list
     """
    attrs = str(attr).split(",")
    key_list = []
    id_list = []
    error_list = []
    event_variables = getdataCenterEventVariables()
    for a in attrs:
        for event in event_variables:
            if event['key'] == a:
                id_list.append(event['id'])
                key_list.append(event['key'])
                break
        else:
            error_list.append(a)
    if len(error_list) == len(attrs):
        logging.error("绑定事件属性失败，事件属性:{}不存在,请先创建事件属性~".format(error_list))
        exit(-1)
    elif len(error_list) != 0:
        logging.error("事件属性:{}不存在,请先创建事件属性~".format(error_list))
    return id_list, key_list
