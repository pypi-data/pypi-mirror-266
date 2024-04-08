# -*- coding:UTF-8 -*-

"""
 @ProjectName  : SwaggerCheck 
 @FileName     : check
 @Description  : 
 @Time         : 2024/3/27 14:50
 @Author       : Qredsun
 """
import copy
import json
import os
import random
import re
import time

import pandas as pd
import requests
from swagger_spec_validator.validator20 import validate_spec

from .expected_code import NecessaryParamMissExpected
from .expected_code import ParamTypeErrorExpected
from .expected_code import ParamValueErrorExpected

from .util import random_string
from .util import RequiredTree
from .util import time_delta_by_days

from .swagger_parser import SwaggerParser

from .log_file import init_log

logger, base_path = init_log('./CheckApiParam')

class CheckApiParam():
    SWAGGER_DATA_BASE_TYPE = ['integer', 'number', 'string', 'datetime', 'boolean', 'null']

    def __init__(self, swagger_doc_url):
        self.swagger_doc = self.corrective_swagger_data(swagger_doc_url)
        self.parser = SwaggerParser(swagger_dict=self.swagger_doc)

        self.necessary_parameter = pd.DataFrame()
        self.parameter_type = pd.DataFrame()
        self.parameter_value = pd.DataFrame()

    @staticmethod
    def corrective_swagger_data(swagger_doc_url):
        # TODO 要处理的 swagger doc 异常问题
        # 1. ref 错误
        # 2. 入参类型为 object
        # 3. 页面展示的参数类型与接口不一致
        # 4. 接口路径中存在基础路径
        temp_file = 'temp.json'

        def save_swagger_from_url(swagger_doc_url):
            try:
                swagger_doc = requests.get(swagger_doc_url).json()
                if swagger_doc is None or 'swagger' not in swagger_doc:
                    raise KeyError(f'{swagger_doc_url} 解析出错！')
                with open(temp_file, 'w', encoding='utf8') as fp:
                    json.dump(swagger_doc, fp, ensure_ascii=False, indent=4)
                return True
            except Exception as e:
                logger.error(f'保存PMS swagger 文档失败：{e}')
                return False

        def read_swagger_from_json(file_name):
            data = { }
            if not os.path.isfile(file_name):
                logger.error(f'{file_name} 不存在')
                return data
            try:
                with open(file_name, encoding='utf-8') as fp:
                    data = json.load(fp)
            except Exception as e:
                logger.error(f'文件{file_name}读取失败：{e}')
            return data

        if save_swagger_from_url(swagger_doc_url):
            swagger_data = read_swagger_from_json(temp_file)
            validate_spec(swagger_data, '')
            return swagger_data
        else:
            raise ValueError('获取swagger数据异常')

    @property
    def host(self):
        return 'http://' + self.swagger_doc.get('host')

    @property
    def title(self):
        return self.swagger_doc.get('info').get('title').replace(' ', '_')

    """ 获取 SwaggerParser 生成的示例参数 """
    def faker_schema_data(self, parameter_info):
        """
        生成 schema 测试数据
        :param parameter_info: 参数描述信息
        :return: api_request_body, definition_key
        """
        api_request_body = None
        original_ref = parameter_info['schema'].get('originalRef', None)
        ref = parameter_info['schema'].get('$ref', None)
        if original_ref or ref:
            if original_ref != self.parser.get_definition_name_from_ref(ref):
                original_ref = self.parser.get_definition_name_from_ref(ref)
                logger.error(f'swagger 文档异常：{ref} {original_ref} 指向不一致, 使用{ref}')

            api_request_body = self.parser.definitions_example.get(original_ref, None)
            logger.debug(f'使用 {original_ref} 获取测试请求 {api_request_body}')

        if not api_request_body:
            api_request_body = { parameter_info['name']: self.parser.get_example_from_prop_spec(parameter_info, None) }
            logger.debug(f'使用 {parameter_info} 获取测试请求 {api_request_body}')

        return api_request_body, original_ref

    @staticmethod
    def find_definition_props(parser, original_ref):
        # 获取接口原定义信息、及必填项
        if not original_ref:
            return None, None
        required_dict = { }
        swager_doc = parser.specification.get('definitions').get(original_ref)
        required_list = swager_doc.get('required', [])
        properties = swager_doc.get('properties', { })

        for properties_name, properties_info in properties.items():
            try:
                if not isinstance(properties_info, dict):
                    properties.update({ properties_name: properties_info })
                    continue
                if properties_info.get('type') == 'array' and 'items' in properties_info:
                    item_original_info = properties_info.get('items')
                    if 'originalRef' in item_original_info or '$ref' in item_original_info:
                        item_original_ref = item_original_info.get('originalRef')
                        item_properties, item_required_tree = CheckApiParam.find_definition_props(parser,
                                                                                                      item_original_ref)
                        properties.update({ properties_name: [item_properties] })
                        if properties_name in required_list:
                            required_list.remove(properties_name)

                        if item_required_tree:
                            required_dict.update({ properties_name: [item_required_tree] })

                    else:
                        item_properties = item_original_info
                        properties.update({ properties_name: [item_properties] })
                        if properties_name in required_list:
                            required_list.remove(properties_name)
                        if 'required' in item_original_info and item_original_info.get('required', False):
                            required_dict.update({ properties_name: [item_properties] })

                if 'originalRef' in properties_info or '$ref' in properties_info:
                    item_original_ref = properties_info.get('originalRef')
                    item_properties, item_required_tree = CheckApiParam.find_definition_props(parser,
                                                                                                  item_original_ref)
                    properties.update({ properties_name: item_properties })
                    if properties_name in required_list:
                        required_list.remove(properties_name)
                    if item_required_tree:
                        required_dict.update({ properties_name: item_required_tree })

            except Exception as e:
                logger.error(f'{original_ref} 参数 {properties_name} 解析失败 {properties_info} ：{e}')

        if required_list or required_dict:
            required_tree = RequiredTree(required_list, required_dict)
        else:
            required_tree = None
        return properties, required_tree

    # 根据必填项生成请求体
    def faker_required_test_body(self, mock_request_body, required_tree):
        # 确认请求体中哪些为必填字段
        if not required_tree:
            logger.debug(f'{mock_request_body} 没有必填参数')
            return None, None

        if required_tree.brothers:
            for param_name in required_tree.brothers:
                # 移除必填项
                test_resquest_body = mock_request_body.copy()
                del test_resquest_body[param_name]
                logger.debug(f'测试body必填项 {param_name} 的请求体：{test_resquest_body}')
                yield test_resquest_body, param_name

        try:
            if required_tree.children:
                for item_name, item_tree in required_tree.children:
                    if isinstance(item_tree, list):
                        test_resquest_body = mock_request_body.copy()
                        # 列表参数
                        for item, changed_param_name in self.faker_required_test_body(test_resquest_body[item_name][0],
                                                                                      item_tree[0]):
                            test_resquest_body[item_name][0] = item
                            yield test_resquest_body, f'{item_name}-{changed_param_name}'
                    else:
                        logger.error(f'required_tree.children 不是列表：{item_tree}')
        except Exception as e:
            logger.error(e)
        logger.debug(f'schema中所有的必填参数已完成测试')

    # 校验响应是否为期望值
    def check_response(self, method, url, parameter_name, api_request_params, api_request_body, expectation):
        api_url = self.host + url
        api_method = method.upper()
        if not api_request_params:
            api_request_params = None
        response = requests.request(api_method, api_url, params=api_request_params, json=api_request_body)
        response = response.json()

        msg = expectation.NOTE
        if 'code' not in response:
            # 异常响应
            logger.warning(f'异常响应体：{response}')
            result_status = 'FAIL'
        else:
            # 验证响应结果
            if response['code'] == 1:
                logger.warning(f'{url} {msg} 验证不通过')
                result_status = 'FAIL'
            elif response['code'] == 0 and response['errorCode'] in expectation.CODES:
                logger.info(f'{url} {msg} 验证通过')
                result_status = 'PASS'
            else:
                logger.error(f'{url} 其他异常：{response}')
                result_status = 'FAIL'

        record = {
            "url"       : url,
            "param_name": parameter_name,
            "param"     : api_request_params,
            "body"      : api_request_body,
            "result"    : result_status,
            "response"  : response
        }
        return record

    # 进行参数校验
    def check_api_parameter(self, urls=[], check_required=True, check_type=True, check_range=True):
        check_necessary_parameter_records = []
        check_parameter_value_records = []
        check_parameter_type_records = []

        for url, info in self.parser.paths.items():
            # url 过滤
            if len(urls) and url not in urls:
                continue
            logger.debug(f'检查接口：{url}')

            for method, v in info.items():
                if not v['parameters']:
                    # 跳过参数为空的url
                    continue

                for parameter_name, parameter_info in v['parameters'].items():
                    try:
                        if check_required:
                            check_necessary_parameter_records.extend(
                                    self.check_necessary_parameter(url, method, v['parameters'], parameter_name,
                                                                   parameter_info))

                        if check_type:
                            check_parameter_type_records.extend(
                                self.check_parameter_type(url, method, v['parameters'], parameter_name, parameter_info))

                        if check_range:
                            check_parameter_value_records.extend(
                                self.check_param_value_range(url, method, v['parameters'], parameter_name,
                                                             parameter_info))
                    except Exception as e:
                        logger.error(f'{url} 参数验证失败： {e}')

        if len(check_necessary_parameter_records):
            self.necessary_parameter = pd.DataFrame(check_necessary_parameter_records)
        if len(check_parameter_type_records):
            self.parameter_type = pd.DataFrame(check_parameter_type_records)
        if len(check_parameter_value_records):
            self.parameter_value = pd.DataFrame(check_parameter_value_records)

    # 必填参数校验
    def check_necessary_parameter(self, url, method, all_parameters, parameter_name, parameter_info):
        if not ('required' in parameter_info and parameter_info['required'] == True):
            # 参数不是必填项跳过
            return []

        # 拼接url
        api_request_body = None
        api_request_params = { }
        request_mocked = False
        check_records = []

        # 发送请求并断言结果
        if parameter_info['in'] == 'header':
            logger.warning(f"参数在header中：{parameter_info} {url}")
        if parameter_info['in'] == 'cookie':
            logger.warning(f"参数在cookie中：{parameter_info} {url}")

        # 生成query请求参数 in = query
        for param_name, param_spec in all_parameters.items():
            if param_spec['in'] != 'query': continue
            api_request_params.update(
                    { param_name: self.parser.get_example_from_prop_spec(param_spec) })

        if not request_mocked and parameter_name in api_request_params:
            del api_request_params[parameter_name]
            request_mocked = True
            logger.debug(f'测试 query 必填项：{parameter_name}')

        # 请求参数 in = path
        if parameter_info['in'] == 'path':
            url = url.format(**{ parameter_name: '' })
            logger.warning(f"测试 path 必填参数在路径中：{parameter_info} {url}")

        # 生成body/json参数 确认参数是否有'schema' in = body
        if 'schema' in parameter_info:
            mock_request_body, original_ref = self.faker_schema_data(parameter_info)
            if not request_mocked:
                properties, required_tree = self.find_definition_props(self.parser, original_ref)
                # 根据必选字段生成验证规则
                for api_request_body, changed_param_name in self.faker_required_test_body(mock_request_body,
                                                                                          required_tree):
                    request_mocked = True
                    check_records.append(self.check_response(method, url, f'{parameter_name}-{changed_param_name}',
                                                             api_request_params, api_request_body,
                                                             NecessaryParamMissExpected))
                # 请求体中没有必填字段
                if not request_mocked:
                    api_request_body = None
                    logger.warning(f'测试缺失请求体 {parameter_name}')
            else:
                api_request_body = mock_request_body

        check_records.append(self.check_response(method, url, parameter_name, api_request_params, api_request_body,
                                                 NecessaryParamMissExpected))
        return check_records

    # 获取与定义不一样的参数类型
    def change_param_type(self, parameter_info):
        if 'enum' in parameter_info.keys():
            while True:
                parameter_value = random.randint(1, 100)
                if parameter_value not in parameter_info['enum']:
                    return parameter_value
        # Object - read from properties, without references
        if parameter_info['type'] == 'object':
            return 'string'
        # Array
        if parameter_info['type'] == 'array':
            return 'string'
        # File
        if parameter_info['type'] == 'file':
            return 'string'

        test_type = self.SWAGGER_DATA_BASE_TYPE.copy()
        # Date time
        if 'format' in parameter_info.keys():
            if parameter_info['format'] == 'date-time' or parameter_info['format'] == 'date':
                test_type.remove('datetime')
                del parameter_info['format']
                parameter_info['type'] = random.choice(test_type)
                return self.parser.get_example_from_prop_spec(parameter_info)
        # 属于基础数据类型
        if parameter_info['type'] in test_type:
            test_type.remove(parameter_info['type'])
            parameter_info['type'] = random.choice(test_type)
            return self.parser.get_example_from_prop_spec(parameter_info)

    # 生成请求体body字段类型
    def faker_test_body_type(self, mock_request_body, properties):
        for param_name, param_spec in properties.items():
            if isinstance(param_spec, dict):
                logger.debug(f'验证参数 {param_name} 数据类型')
                if 'type' not in param_spec:
                    """ SwaggerParser 根据定义生成的示例缺丢失了部分参数  """
                    if param_name in mock_request_body:
                        mock_request_body_t = mock_request_body[param_name]
                    else:
                        mock_request_body_t = mock_request_body
                    properties_t = param_spec
                    for item, changed_param in self.faker_test_body_type(mock_request_body_t, properties_t):
                        temp_body = copy.deepcopy(mock_request_body)
                        temp_body[param_name] = item
                        yield temp_body, f'{param_name}-{changed_param}'
                else:
                    temp_body = copy.deepcopy(mock_request_body)
                    temp_body.update({ param_name: self.change_param_type(param_spec) })
                    yield temp_body, param_name
            elif isinstance(param_spec, list):
                """ SwaggerParser 根据定义生成的示例缺丢失了部分参数  """
                if param_name in mock_request_body:
                    # 将列表转为字典
                    mock_request_body_t = { param_name: mock_request_body[param_name][0] }
                else:
                    mock_request_body_t = mock_request_body
                properties_t = { param_name: param_spec[0] }
                for item, changed_param in self.faker_test_body_type(mock_request_body_t, properties_t):
                    temp_body = copy.deepcopy(mock_request_body)
                    temp_body[param_name] = [item[param_name]]
                    yield temp_body, f'{param_name}[0]-{changed_param}'
                temp_body.update({ param_name: 'string' })
                yield temp_body, param_name
            else:
                logger.warning(f'待处理参数 {param_spec}')

    # 参数类型校验
    def check_parameter_type(self, url, method, all_parameters, parameter_name, parameter_info):
        # 拼接url
        api_request_body = None
        api_request_params = { }
        request_mocked = False
        check_records = []

        # 发送请求并断言结果
        if parameter_info['in'] == 'header':
            logger.warning(f"参数在header中：{parameter_info} {url}")
        if parameter_info['in'] == 'cookie':
            logger.warning(f"参数在cookie中：{parameter_info} {url}")

        # 生成query请求参数 in = query
        for param_name, param_spec in all_parameters.items():
            if param_spec['in'] != 'query': continue
            api_request_params.update(
                    { param_name: self.parser.get_example_from_prop_spec(param_spec) })

        if not request_mocked and parameter_name in api_request_params:
            api_request_params.update({ param_name: self.change_param_type(parameter_info) })
            request_mocked = True
            logger.debug(f'测试query 参数 {parameter_name} 的类型校验')

        # 请求参数 in = path
        if parameter_info['in'] == 'path':
            right_url = url.format(**{ parameter_name: self.parser.get_example_from_prop_spec(parameter_info) })
            logger.debug(f'正常测 path 值：{right_url}')
            url = url.format(**{ parameter_name: self.change_param_type(parameter_info) })
            logger.warning(f"测试 path 参数类型时：{parameter_info} {url}")

        # 生成body/json参数 确认参数是否有'schema' in = body
        if 'schema' in parameter_info:
            mock_request_body, original_ref = self.faker_schema_data(parameter_info)
            if not request_mocked:
                if original_ref:
                    # schema 中没有 ref
                    properties, required_tree = self.find_definition_props(self.parser, original_ref)
                else:
                    # 构造properties
                    properties = { parameter_info['name']: parameter_info['schema'] }
                # 根据必选字段生成验证规则
                for api_request_body, changed_param in self.faker_test_body_type(mock_request_body, properties):
                    request_mocked = True
                    check_records.append(self.check_response(method, url, changed_param, api_request_params,
                                                             api_request_body, ParamTypeErrorExpected))

                # 请求体中没有字段
                if not request_mocked:
                    api_request_body = None
                    logger.warning(f'测试请求体 {parameter_name} 类型')
            else:
                api_request_body = mock_request_body

        check_records.append(self.check_response(method, url, parameter_name, api_request_params,
                                                 api_request_body, ParamTypeErrorExpected, ))
        return check_records

    # 生成和正则不匹配的字符串
    def _not_regex_string(self, pattern):
        regex = re.compile(pattern)
        while True:
            random_string = random_string(length=random.randint(1, 100))
            if regex.findall(random_string):
                return random_string

    # 获取边界值
    def param_range_values(self, parameter_info):
        params = []
        # 最小值
        if 'minimum' in parameter_info:
            if 'type' in parameter_info.keys() and parameter_info['type'] == 'integer' or parameter_info[
                'type'] == 'number':
                params.append(parameter_info['minimum'] - 1)
            if 'format' in parameter_info.keys():
                if parameter_info['format'] == 'date-time':
                    # time_format = "%Y-%m-%d %H:%M:%S"
                    time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
                    params.append(time_delta_by_days(parameter_info['minimum'], -1, time_format))
                if parameter_info['format'] == 'date':
                    time_format = "%Y-%m-%d"
                    params.append(time_delta_by_days(parameter_info['minimum'], -1, time_format))
        # 最大值
        if 'maximum' in parameter_info:
            if 'type' in parameter_info.keys() and parameter_info['type'] == 'integer' or parameter_info[
                'type'] == 'number':
                params.append(parameter_info['maximum'] + 1)
            if 'format' in parameter_info.keys():
                if parameter_info['format'] == 'date-time':
                    time_format = "%Y-%m-%d %H:%M:%S"
                    params.append(time_delta_by_days(parameter_info['maximum'], 1, time_format))
                if parameter_info['format'] == 'date':
                    time_format = "%Y-%m-%d"
                    params.append(time_delta_by_days(parameter_info['maximum'], 1, time_format))
        # 最小长度
        if 'minLength' in parameter_info:
            params.append(random_string(int(parameter_info['minLength']) - 1))
        # 最大长度
        if 'maxLength' in parameter_info:
            params.append(random_string(int(parameter_info['maxLength']) + 1))
        # 正则
        if 'pattern' in parameter_info:
            params.append(self._not_regex_string(parameter_info['pattern']))
        # 允许为空
        if 'allowEmptyValue' in parameter_info.keys() and not parameter_info['allowEmptyValue']:
            params.append('')
        return params

    # 请求体body字段值边界
    def faker_test_body_valus(self, mock_request_body, properties):
        for param_name, param_spec in properties.items():
            if isinstance(param_spec, dict):
                logger.debug(f'验证参数 {param_name} 数据类型')
                if 'type' not in param_spec:
                    """ SwaggerParser -BUG 根据定义生成的示例缺丢失了部分参数  """
                    if param_name in mock_request_body:
                        mock_request_body_t = mock_request_body[param_name]
                    else:
                        mock_request_body_t = mock_request_body
                    properties_t = param_spec
                    for item, changed_param in self.faker_test_body_valus(mock_request_body_t, properties_t):
                        temp_body = copy.deepcopy(mock_request_body)
                        temp_body[param_name] = item
                        yield temp_body, f'{param_name}-{changed_param}'
                else:
                    for value in self.param_range_values(param_spec):
                        temp_body = copy.deepcopy(mock_request_body)
                        temp_body.update({ param_name: value })
                        yield temp_body, param_name
            elif isinstance(param_spec, list):
                """ SwaggerParser -BUG 根据定义生成的示例缺丢失了部分参数  """
                if param_name in mock_request_body:
                    mock_request_body_t = { param_name: mock_request_body[param_name][0] }  # 将列表转为字典
                else:
                    mock_request_body_t = mock_request_body  # 将列表转为字典

                properties_t = { param_name: param_spec[0] }
                for item, changed_param in self.faker_test_body_valus(mock_request_body_t, properties_t):
                    temp_body = copy.deepcopy(mock_request_body)
                    temp_body[param_name] = [item[param_name]]
                    yield temp_body, f'{param_name}[0]-{changed_param[len(param_name) - 1:]}'
            else:
                logger.warning('待处理参数')

    # 值的范围
    def check_param_value_range(self, url, method, all_parameters, parameter_name, parameter_info):
        # 拼接url
        api_request_body = None
        api_request_params = { }
        request_mocked = False
        check_records = []

        # 验证参数值列表
        list_api_request_params = []  # query
        list_api_request_url = []  # path

        # 发送请求并断言结果
        if parameter_info['in'] == 'header':
            logger.warning(f"参数在header中：{parameter_info} {url}")
        if parameter_info['in'] == 'cookie':
            logger.warning(f"参数在cookie中：{parameter_info} {url}")

        # 生成query请求参数 in = query
        for param_name, param_spec in all_parameters.items():
            if param_spec['in'] != 'query': continue
            api_request_params.update(
                    { param_name: self.parser.get_example_from_prop_spec(param_spec) })

        if not request_mocked and parameter_name in api_request_params:
            for value in self.param_range_values(parameter_info):
                temp = api_request_params.copy()
                temp.update({ param_name: value })
                list_api_request_params.append(temp)
            if not list_api_request_params:
                logger.debug(f'query 参数 {param_name} 没有取值范围限制')
                return check_records
            request_mocked = True
            logger.debug(f'测试query 参数 {parameter_name} 的值校验')

        # 请求参数 in = path
        if parameter_info['in'] == 'path':
            for value in self.param_range_values(parameter_info):
                list_api_request_url.append(url.format(**{ parameter_name: value }))
            if not list_api_request_params:
                logger.debug(f'path 参数 {param_name} 没有取值范围限制')
                return check_records
            request_mocked = True
            logger.warning(f"测试 path 参数 {param_name} 值校验：{list_api_request_url}")

        # 生成body/json参数 确认参数是否有 'schema' in = body
        if 'schema' in parameter_info:
            mock_request_body, original_ref = self.faker_schema_data(parameter_info)
            if request_mocked:
                api_request_body = mock_request_body
            else:
                if original_ref:  # schema 中没有 ref
                    properties, required_tree = self.find_definition_props(self.parser, original_ref)
                else:
                    # 构造properties
                    properties = { parameter_info['name']: parameter_info['schema'] }
                # 根据必选字段生成验证规则
                for api_request_body, changed_param in self.faker_test_body_valus(mock_request_body, properties):
                    request_mocked = True
                    check_records.append(self.check_response(method, url, changed_param, api_request_params,
                                                             api_request_body, ParamValueErrorExpected))

                # 请求体中所有字段都没有指定取值范围
                if not request_mocked:
                    return check_records

        for param_name in list_api_request_params:
            check_records.append(self.check_response(method, url, parameter_name, param_name,
                                                     api_request_body, ParamValueErrorExpected, ))
        for request_url in list_api_request_url:
            check_records.append(self.check_response(method, request_url, parameter_name, api_request_params,
                                                     api_request_body, ParamValueErrorExpected, ))
        return check_records

    def save_result(self, save_dir = '.'):
        """
        保存验证结果
        保存内容：
        |url|校验项|结果|入参|响应信息
        """
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, time.strftime(f"%Y_%m_%d_%H-{self.title}.xlsx"))
        if not (self.necessary_parameter.shape[0] or self.parameter_type.shape[0] or self.parameter_value.shape[0]):
            logger.info('验证记录为空，不需要保存')
            return

        writer = pd.ExcelWriter(save_path)
        if self.necessary_parameter.shape[0]:
            self.necessary_parameter.to_excel(writer, sheet_name=NecessaryParamMissExpected.NOTE, index=False)
        if self.parameter_value.shape[0]:
            self.parameter_value.to_excel(writer, sheet_name=ParamValueErrorExpected.NOTE, index=False)
        if self.parameter_type.shape[0]:
            self.parameter_type.to_excel(writer, sheet_name=ParamTypeErrorExpected.NOTE, index=False)
        writer.close()
        logger.info(f'保存验证记录至：{save_path}')


if __name__ == '__main__':
    swagger_doc_url = 'http://dev-nginx-swagger.com'
    c = CheckApiParam(swagger_doc_url)
    c.check_api_parameter()
    c.save_result()
