# -*- coding: utf-8 -*-

API_HOST = 'http://8.130.48.76:16801'  # 数据处理操作Host

_config = {
    'default_api_host': API_HOST,
    'connection_timeout': 30,  # 链接超时为时间为30s
    'connection_retries': 3,  # 链接重试次数为3次
    'connection_pool': 10  # 链接池个数为10
}

_is_customized_default = {
    'default_api_host': False,
    'connection_timeout': False,
    'connection_retries': False,
    'connection_pool': False
}


def is_customized_default(key):
    return _is_customized_default[key]


def get_default(key):
    return _config[key]


def set_default(
        connection_retries=None, connection_pool=None, connection_timeout=None,
        default_api_host=None):
    if default_api_host:
        _config['default_api_host'] = default_api_host
        _is_customized_default['default_api_host'] = True
    if connection_retries:
        _config['connection_retries'] = connection_retries
        _is_customized_default['connection_retries'] = True
    if connection_pool:
        _config['connection_pool'] = connection_pool
        _is_customized_default['connection_pool'] = True
    if connection_timeout:
        _config['connection_timeout'] = connection_timeout
        _is_customized_default['connection_timeout'] = True