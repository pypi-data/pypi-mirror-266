import json

from importers.common.http_util import send_graphql_post
from importers.common.log_util import my_logger
from importers.meta.check_util import *
from importers.meta.data_center import getMetaData, getBindEvent

"""
元数据创建
"""


def create_event(key, name, desc):
    """
       创建事件
    """
    names = check_name(name, key)
    flag, var, id_list = check_event_attr_exsit(key)
    str_sub = ''
    if len(id_list) != 0:
        attr_str = ''
        for i in range(len(id_list)):
            attr_str += '{\"type\":\"EVENT_VARIABLE\",\"id\":\"' + str(id_list[i]) + '\"},'
        str_sub = attr_str[:len(attr_str) - 1]
    if flag:
        if desc == '' and name != '':
            body = """{"operationName":"updateDataCenterCustomEvent","variables":{"customEvent":{"attributes":[%s],"valueType":"counter","description":"%s","key":"%s","name":"%s"},
                   "id":"%s"},"query":"mutation updateDataCenterCustomEvent($id: HashId!, $customEvent: CustomEventInput!) {updateDataCenterCustomEvent(id: $id, customEvent: $customEvent) 
                   {name    __typename}}"}""" % (str_sub, var['description'], key, var['name'], var['id'])
        elif names == key and desc != '':
            body = """{"operationName":"updateDataCenterCustomEvent","variables":{"customEvent":{"attributes":[%s],"valueType":"counter","description":"%s","key":"%s","name":"%s"},
                   "id":"%s"},"query":"mutation updateDataCenterCustomEvent($id: HashId!, $customEvent: CustomEventInput!) {updateDataCenterCustomEvent(id: $id, customEvent: $customEvent) 
                   {name    __typename}}"}""" % (str_sub, desc, key, var['name'], var['id'])
        elif name != '' and desc != '':
            body = """{"operationName":"updateDataCenterCustomEvent","variables":{"customEvent":{"attributes":[%s],"valueType":"counter","description":"%s","key":"%s","name":"%s"},
                   "id":"%s"},"query":"mutation updateDataCenterCustomEvent($id: HashId!, $customEvent: CustomEventInput!) {updateDataCenterCustomEvent(id: $id, customEvent: $customEvent) 
                   {name    __typename}}"}""" % (str_sub, desc, key, names, var['id'])
        else:
            body = """{"operationName":"updateDataCenterCustomEvent","variables":{"id":"%s","customEvent":{"name":"%s","key":"%s","description":"%s",
             "valueType":"counter","attributes":[%s]}},"query":"mutation updateDataCenterCustomEvent($id: HashId!, $customEvent: CustomEventInput!) 
             {  updateDataCenterCustomEvent(id: $id, customEvent: $customEvent) {    name    __typename  }}"}""" % (
                var['id'], var['name'], key, var['description'], str_sub)
    else:
        body = """{"operationName":"createDataCenterCustomEvent","variables":{"customEvent":{"attributes":[],"valueType":"counter",
            "key":"%s","name":"%s","description":"%s"}},"query":"mutation createDataCenterCustomEvent($customEvent: CustomEventInput!) 
            {createDataCenterCustomEvent(customEvent: $customEvent) {name    __typename }}"}""" % (key, name, desc)
    content = send_graphql_post(body.encode('utf-8'))
    return content


# 创建事件属性
def create_event_variables(key, valuetype, name, desc):
    """
       创建事件属性
    """
    name = check_name(name, key)
    check_event_valuetype(valuetype)
    flag, var = check_event_var_exsit(key)
    if flag:
        if desc == '':
            body = """{"operationName":"updateDataCenterEventVariable","variables":{"id":"%s","eventVariable":{"name":"%s","key":"%s",
                    "description":"%s","valueType":"%s"}},"query":"mutation updateDataCenterEventVariable($id: HashId!, $eventVariable: VariableInput!) 
                    {  updateDataCenterEventVariable(id: $id, eventVariable: $eventVariable) {    name    __typename  }}"}""" % (
                var['id'], name, key, var['description'], var['valueType'])
        elif name == key:
            body = """{"operationName":"updateDataCenterEventVariable","variables":{"id":"%s","eventVariable":{"name":"%s","key":"%s",
                     "description":"%s","valueType":"%s"}},"query":"mutation updateDataCenterEventVariable($id: HashId!, $eventVariable: VariableInput!) 
                     {  updateDataCenterEventVariable(id: $id, eventVariable: $eventVariable) {    name    __typename  }}"}""" % (
                var['id'], var['name'], key, desc, var['valueType'])
        else:
            body = """{"operationName":"updateDataCenterEventVariable","variables":{"id":"%s","eventVariable":{"name":"%s","key":"%s",
                     "description":"%s","valueType":"%s"}},"query":"mutation updateDataCenterEventVariable($id: HashId!, $eventVariable: VariableInput!) 
                     {  updateDataCenterEventVariable(id: $id, eventVariable: $eventVariable) {    name    __typename  }}"}""" % (
                var['id'], name, key, desc, var['valueType'])
        content = send_graphql_post(body.encode('utf-8'))
        my_logger.info("事件属性存在且更新成功")
    else:
        body = """{"operationName":"createDataCenterEventVariable","variables":{"eventVariable":{"name":"%s","key":"%s",
        "valueType":"%s","description":"%s"}},"query":"mutation createDataCenterEventVariable($eventVariable: VariableInput!) 
        {createDataCenterEventVariable(eventVariable: $eventVariable) {name    __typename}}"}""" % (
            name, key, valuetype, desc)
        content = send_graphql_post(body.encode('utf-8'))
    return content


# 创建用户属性
def create_user_variables(key, valuetype, name, desc):
    """
       创建用户属性
    """
    name = check_name(name, key)
    check_user_valuetype(valuetype)
    flag, var = check_user_var_exsit(key)
    if flag:
        if desc == '':
            body = """{"operationName":"updateDataCenterUserVariable","variables":{"id":"%s","userVariable":{"name":"%s","key":"%s","description":"%s",
            "valueType":"%s"}},"query":"mutation updateDataCenterUserVariable($id: HashId!, $userVariable: VariableInput!) {  updateDataCenterUserVariable(id: $id,
             userVariable: $userVariable) {    name    __typename  }}"}""" % (
                var['id'], name, key, var['description'], var['valueType'])
        elif name == key:
            body = """{"operationName":"updateDataCenterUserVariable","variables":{"id":"%s","userVariable":{"name":"%s","key":"%s","description":"%s",
             "valueType":"%s"}},"query":"mutation updateDataCenterUserVariable($id: HashId!, $userVariable: VariableInput!) {  updateDataCenterUserVariable(id: $id,
             userVariable: $userVariable) {    name    __typename  }}"}""" % (
                var['id'], var['name'], key, desc, var['valueType'])
        else:
            body = """{"operationName":"updateDataCenterUserVariable","variables":{"id":"%s","userVariable":{"name":"%s","key":"%s","description":"%s",
            "valueType":"%s"}},"query":"mutation updateDataCenterUserVariable($id: HashId!, $userVariable: VariableInput!) {  updateDataCenterUserVariable(id: $id,
            userVariable: $userVariable) {    name    __typename  }}"}""" % (
                var['id'], name, key, desc, var['valueType'])
        content = send_graphql_post(body.encode('utf-8'))
        my_logger.info("用户属性存在且更新成功")
    else:
        body = """{"operationName":"createDataCenterUserVariable","variables":{"userVariable":{"name":"%s","key":"%s","valueType":"%s","description":"%s"}},
        "query":"mutation createDataCenterUserVariable($userVariable: VariableInput!) {createDataCenterUserVariable(userVariable: $userVariable) {
            id    name    __typename  }}"}""" % (name, key, valuetype, desc)
        content = send_graphql_post(body.encode('utf-8'))
    return content


def bind_event_variables(key, name, attr):
    """
        绑定事件与事件属性
    """
    id_list, key_list = check_attr(attr)
    flag, var, attr_id_list = check_event_attr_exsit(key)
    name = check_name(name, key)
    attr_str = ''
    size = len(id_list)
    for i in range(size):
        attr_str += '{\"type\":\"EVENT_VARIABLE\",\"id\":\"' + str(id_list[i]) + '\"},'
    str_sub = attr_str[:len(attr_str) - 1]
    if flag and len(attr_id_list) > 0:
        body = """{"operationName":"updateDataCenterCustomEvent","variables":{"customEvent":{"attributes":[%s],"valueType":"counter","description":"%s","key":"%s","name":"%s"},
        "id":"%s"},"query":"mutation updateDataCenterCustomEvent($id: HashId!, $customEvent: CustomEventInput!) {updateDataCenterCustomEvent(id: $id, customEvent: $customEvent)
         {   name  __typename  }}"}""" % (str_sub, var['description'], key, var['name'], var['id'])
    elif flag and len(attr_id_list) == 0:
        body = """{"operationName":"updateDataCenterCustomEvent","variables":{"customEvent":{"attributes":[%s],"valueType":"counter","description":"%s","key":"%s","name":"%s"},
        "id":"%s"},"query":"mutation updateDataCenterCustomEvent($id: HashId!, $customEvent: CustomEventInput!) {updateDataCenterCustomEvent(id: $id, customEvent: $customEvent) 
        {name    __typename}}"}""" % (str_sub, var['description'], key, var['name'], var['id'])
    else:
        body = """{"operationName":"createDataCenterCustomEvent","variables":{"customEvent":{"attributes":[%s],"valueType":"counter",
        "key":"%s","name":"%s"}},"query":"mutation createDataCenterCustomEvent($customEvent: CustomEventInput!) {createDataCenterCustomEvent(customEvent: $customEvent) {
        name    __typename }}"}""" % (str_sub, key, name)
    content = send_graphql_post(body.encode('utf-8'))
    return content, key_list


def export_meta(file):
    """
       导出元数据
    """
    meta_data = getMetaData()
    meta_data['events'] = meta_data.pop('dataCenterCustomEvents')
    meta_data['event_variables'] = meta_data.pop('dataCenterEventVariables')
    meta_data['user_variables'] = meta_data.pop('dataCenterUserVariables')
    user_attr_list = list()
    for i in meta_data['user_variables']:
        if not str(i['key']).startswith("$"):
            user_attr_list.append(i)
    meta_data['user_variables'] = user_attr_list

    event_list = list()
    for i in meta_data['events']:
        if not str(i['key']).startswith("$"):
            event_list.append(i)
    meta_data['events'] = event_list

    event_attr_list = list()
    for i in meta_data['event_variables']:
        if not str(i['key']).startswith("$"):
            event_attr_list.append(i)
    meta_data['event_variables'] = event_attr_list
    meta_data = str(meta_data).replace('\'', '\"').replace('\\', '\\\\')[:-1]
    event = getBindEvent()
    event_vars_list = list()
    event['bind_event_variables'] = event.pop('dataCenterCustomEvents')
    for i in event['bind_event_variables']:
        if not str(i['key']).startswith("$") and len(i['attributes']) != 0:
            event_vars_list.append(i)
    event['bind_event_variables'] = event_vars_list
    event = str(event).replace('\'', '\"').replace('\\', '\\\\')[1:]
    json_str = meta_data + ',' + event
    with open(file, 'w+', encoding='utf-8') as f:
        f.write(json_str.encode('utf-8').decode('utf-8'))
        # json.dump(json.loads(json_str), f)
    my_logger.info("导出元数据成功~")


def import_meta(file):
    """
       导入元数据
    """
    with open(file, 'r', encoding='utf-8') as f:
        json_loads = json.loads(f.read())
        if len(json_loads['events']) != 0:
            for event in json_loads['events']:
                check_key(event['key'])
                create_event(event['key'], event['name'], event['description'])
        if len(json_loads['event_variables']) != 0:
            for var in json_loads['event_variables']:
                check_key(var['key'])
                create_event_variables(var['key'], str(var['valueType']).lower(), var['name'],
                                       var['description'])
        if len(json_loads['user_variables']) != 0:
            for var in json_loads['user_variables']:
                check_key(var['key'])
                create_user_variables(var['key'], str(var['valueType']).lower(), var['name'], var['description'])
        if len(json_loads['bind_event_variables']) != 0:
            for var in json_loads['bind_event_variables']:
                attr_str = ''
                for attr in var['attributes']:
                    attr_str += str(attr['key']) + ','
                sub_attr = attr_str[:-1]
                if len(sub_attr) > 2:
                    bind_event_variables(var['key'], '', sub_attr)
    my_logger.info("导入元数据成功~")


def create_item(item_key, analysis, name, desc):
    """
       创建主体
    """
    names = check_name(name, item_key)
    check_item_key(item_key)
    desc = check_desc(desc)
    flag, var_id, var_name, var_desc = check_item_var_exsit(item_key)
    if name != var_name:
        check_item_name_exsit(name)
    if flag:
        if desc == '' and name != '':
            body = """{"operationName":"updateDataCenterItemModel","variables":{"itemModel":{"description":"%s","name":"%s"},
                        "id":"%s"},"query":"mutation updateDataCenterItemModel($id: HashId!, $itemModel: ItemModelInput!)
                        {\n  updateDataCenterItemModel(id: $id, itemModel: $itemModel) {\n    name\n    __typename\n  }\n}\n"}""" \
                   % (var_desc, name, var_id)
            content = send_graphql_post(body.encode('utf-8'))
            my_logger.info("主体存在且更新成功")
        elif names == item_key and desc != '':
            body = """{"operationName":"updateDataCenterItemModel","variables":{"itemModel":{"description":"%s","name":"%s"},
                                    "id":"%s"},"query":"mutation updateDataCenterItemModel($id: HashId!, $itemModel: ItemModelInput!)
                                    {\n  updateDataCenterItemModel(id: $id, itemModel: $itemModel) {\n    name\n    __typename\n  }\n}\n"}""" \
                   % (desc, var_name, var_id)
            content = send_graphql_post(body.encode('utf-8'))
            my_logger.info("主体存在且更新成功")
        elif names == item_key and desc == '':
            body = """{"operationName":"updateDataCenterItemModel","variables":{"itemModel":{"description":"%s","name":"%s"},
                                    "id":"%s"},"query":"mutation updateDataCenterItemModel($id: HashId!, $itemModel: ItemModelInput!)
                                    {\n  updateDataCenterItemModel(id: $id, itemModel: $itemModel) {\n    name\n    __typename\n  }\n}\n"}""" \
                   % (var_desc, var_name, var_id)
            content = send_graphql_post(body.encode('utf-8'))
            my_logger.info("主体存在且更新成功")
        else:
            body = """{"operationName":"updateDataCenterItemModel","variables":{"itemModel":{"description":"%s","name":"%s"},
            "id":"%s"},"query":"mutation updateDataCenterItemModel($id: HashId!, $itemModel: ItemModelInput!)
            {\n  updateDataCenterItemModel(id: $id, itemModel: $itemModel) {\n    name\n    __typename\n  }\n}\n"}""" \
                   % (desc, name, var_id)
            content = send_graphql_post(body.encode('utf-8'))
            my_logger.info("主体存在且更新成功")
    else:
        check_item_name_exsit(name)
        if analysis:
            body = """{"operationName":"createDataCenterItemModel","variables":{"itemModel":{"attributes":[{
            "valueType":"string","description":"%s","isPrimaryKey":true,"key":"%s","name":"%s"}],
            "description":"%s","name":"%s", "analysis": true}}, "query":"mutation createDataCenterItemModel($itemModel: 
            ItemModelInput!) {\n  createDataCenterItemModel(itemModel: $itemModel) {\n    name\n    id\n    
            __typename\n  }\n}\n"}""" % (
                desc, item_key, name, desc, name)
            content = send_graphql_post(body.encode('utf-8'))
            my_logger.info("分析主体创建成功:", content)
        else:
            body = """{"operationName":"createDataCenterItemModel","variables":{"itemModel":{"attributes":[{
            "valueType":"string","description":"%s","isPrimaryKey":true,"key":"%s","name":"%s"}],"description":"%s",
            "name":"%s"}}, "query":"mutation createDataCenterItemModel($itemModel: ItemModelInput!) {\n  
            createDataCenterItemModel(itemModel: $itemModel) {\n    name\n    id\n    __typename\n  }\n}\n"}""" % (
                desc, item_key, name, desc, name)
            content = send_graphql_post(body.encode('utf-8'))
            my_logger.info("字典表创建成功:", content)
    return content


def import_item_variables(item_key, analysis, file):
    """
       导入主体字段
    """
    flag, var_id, var_name, var_desc = check_item_var_exsit(item_key)
    if flag:
        with open(file, 'r', encoding='utf-8') as f:
            json_loads = json.loads(f.read())
            for item in json_loads['attributes']:
                create_item(item_key, analysis, json_loads['name'], json_loads['description'])
                create_item_variables(var_id, item['key'], item['name'], item['valueType'], item['description'])
    else:
        with open(file, 'r', encoding='utf-8') as f:
            json_loads = json.loads(f.read())
            name = json_loads['name']
            desc = json_loads['description']
            create_item(item_key, analysis, name, desc)
            flag, var_id, var_name, var_desc = check_item_var_exsit(item_key)
            for item in json_loads['attributes']:
                check_key(item['key'])
                create_item_variables(var_id, item['key'], item['name'], item['valueType'], item['description'])


def create_item_variables(old_id, key, name, valueType, desc):
    check_item_key_variables(key)
    names = check_name(name, key)
    desc = check_desc(desc)
    flag, var_name, var_valueType, var_desc, new_id = check_item_var_key_exsit(old_id, key)
    if name != var_name:
        check_item_name_exsit(name)
    if flag:
        if valueType != var_valueType:
            logging.error("主体属性<{}>类型不可更新".format(key))
            exit(-1)
        if desc == '' and name != '':
            body = """{"operationName":"updateDataCenterItemVariable",
            "variables":{"itemVariable":{"description":"%s","valueType":"%s","key":"%s","name":"%s"},
            "id":"%s"},"query":"mutation updateDataCenterItemVariable($id: HashId!, $itemVariable: VariableInput!) 
            {\n  updateDataCenterItemVariable(id: $id, itemVariable: $itemVariable) {\n    name\n    __typename\n  }\n}\n"}
            """ % (var_desc, var_valueType, key, name, new_id)
            content = send_graphql_post(body.encode('utf-8'))
            my_logger.info("主体属性存在且更新成功")
        elif names == key and desc != '':
            body = """{"operationName":"updateDataCenterItemVariable",
                        "variables":{"itemVariable":{"description":"%s","valueType":"%s","key":"%s","name":"%s"},
                        "id":"%s"},"query":"mutation updateDataCenterItemVariable($id: HashId!, $itemVariable: VariableInput!) 
                        {\n  updateDataCenterItemVariable(id: $id, itemVariable: $itemVariable) {\n    name\n    __typename\n  }\n}\n"}
                        """ % (desc, var_valueType, key, var_name, new_id)
            content = send_graphql_post(body.encode('utf-8'))
            my_logger.info("主体属性存在且更新成功")
        else:
            body = """{"operationName":"updateDataCenterItemVariable",
                                    "variables":{"itemVariable":{"description":"%s","valueType":"%s","key":"%s","name":"%s"},
                                    "id":"%s"},"query":"mutation updateDataCenterItemVariable($id: HashId!, $itemVariable: VariableInput!) 
                                    {\n  updateDataCenterItemVariable(id: $id, itemVariable: $itemVariable) {\n    name\n    __typename\n  }\n}\n"}
                                    """ % (desc, var_valueType, key, name, new_id)
            content = send_graphql_post(body.encode('utf-8'))
            my_logger.info("主体属性存在且更新成功")
    else:
        check_item_name_exsit(name)
        check_item_key_exsit(key)
        check_item_valuetype(valueType)
        body = """{"operationName":"createDataCenterItemVariable","variables"
                    :{"attribute":{"isPrimaryKey":false,"description":"%s","valueType":"%s","key":"%s","name":"%s"}
                    ,"id":"%s"},"query":"mutation createDataCenterItemVariable($id: HashId!, $attribute: ItemVariableInput!) 
                    {\n  dataCenterAddItemModelAttribute(id: $id, attribute: $attribute) {\n    name\n    __typename\n  }\n}\n"}
                    """ % (desc, valueType, key, name, old_id)
        content = send_graphql_post(body.encode('utf-8'))
        my_logger.info("主体属性创建成功:", content)

    return content
