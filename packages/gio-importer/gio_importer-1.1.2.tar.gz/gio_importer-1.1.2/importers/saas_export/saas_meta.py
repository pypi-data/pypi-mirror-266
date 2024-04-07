"""
SaaS元数据
"""
import json

from importers.common.config_util import SaasConfig
from importers.common.http_util import send_rest_get


def getSaasMeta(file):
    """
      导出SaaS元数据
     """
    events = 'v1/api/projects/' + SaasConfig.uid + '/dim/events'
    event_vars = 'v1/api/projects/' + SaasConfig.uid + '/vars/events'
    user_vars = 'v1/api/projects/' + SaasConfig.uid + '/vars/peoples'
    anonymous_var = 'v1/api/projects/' + SaasConfig.uid + '/vars/visitors'
    parmas = {'project_uid': SaasConfig.uid}
    events_context = send_rest_get(events, parmas)
    event_var_context = send_rest_get(event_vars, parmas)
    usr_var_context = send_rest_get(user_vars, parmas)
    anonymous_var_context = send_rest_get(anonymous_var, parmas)
    # 事件
    event_list = []
    result = {}
    for data in events_context:
        event_res = {}
        event_res['key'] = data['key'].strip()
        event_res['name'] = data['name'].strip()
        event_res['description'] = data['description'].strip()
        event_list.append(event_res)
    result['events'] = event_list
    # 事件属性
    evar_list = []
    for evar in event_var_context:
        evar_res = {}
        evar_res['key'] = evar['key'].strip()
        evar_res['name'] = evar['name'].strip()
        evar_res['valueType'] = str(evar['type']).lower().strip()
        evar_res['description'] = ''
        evar_list.append(evar_res)
    result['event_variables'] = evar_list
    # 用户属性
    uvar_list = []
    uvar_set = set()
    for uvar in usr_var_context:
        uvar_res = {}
        uvar_res['key'] = uvar['key'].strip()
        uvar_res['name'] = uvar['name'].strip()
        uvar_res['valueType'] = 'string'
        uvar_res['description'] = uvar['description'].strip()
        uvar_list.append(uvar_res)
        uvar_set.add(uvar['key'].strip())
    uvar_size = len(uvar_set)

    # 访问用户属性
    avar_list = []
    avar_set = set()
    for avar in anonymous_var_context:
        avar_res = {}
        avar_res['key'] = avar['key'].strip()
        avar_res['name'] = avar['name'].strip()
        avar_res['valueType'] = 'string'
        avar_res['description'] = avar['description'].strip()
        avar_list.append(avar_res)
        avar_set.add(avar['key'].strip())
    avar_size = len(avar_set)

    var_set = set()
    for var in avar_set:
        if var not in uvar_set:
            var_set.add(var)
    if uvar_size + avar_size == len(uvar_set | var_set):
        result['user_variables'] = uvar_list + avar_list
    else:
        for i in avar_list:
            if i['key'] in var_set:
                uvar_list.append(i)
        result['user_variables'] = uvar_list

    attr_list = []
    for data in events_context:
        event_res = {}
        list = []
        for attr in data['attrs']:
            item = {}
            item['key'] = attr['key'].strip()
            list.append(item)
        event_res['key'] = data['key'].strip()
        event_res['attributes'] = list
        attr_list.append(event_res)
    result['bind_event_variables'] = attr_list
    json_str = str(result).replace('\'', '\"')
    with open(file, "w+", encoding='utf-8') as f:
        f.write(json_str.encode('utf-8').decode('utf-8'))
    print("事件，事件属性，用户属性导出成功~")
