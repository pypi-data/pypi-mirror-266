# -*- coding: utf-8 -*-
import functools
import logging
import platform

from requests.adapters import HTTPAdapter

from sparkproxy import config, __version__
from .client import HTTPClient
from .middleware import UserAgentMiddleware
from .response import ResponseInfo

qn_http_client = HTTPClient(
    middlewares=[
        UserAgentMiddleware(__version__)
    ]
)


# compatibility with some config from sparkproxy.config
def _before_send(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if _session is None:
            _init()
        return func(self, *args, **kwargs)

    return wrapper


qn_http_client.send_request = _before_send(qn_http_client.send_request)

_sys_info = '{0}; {1}'.format(platform.system(), platform.machine())
_python_ver = platform.python_version()

USER_AGENT = 'SparkProxyPython/{0} ({1}; ) Python/{2}'.format(
    __version__, _sys_info, _python_ver)

_session = None
_headers = {'User-Agent': USER_AGENT}


def __return_wrapper(resp):
    if resp.status_code != 200:
        return None, ResponseInfo(resp)
    resp.encoding = 'utf-8'
    try:
        ret = resp.json()
    except ValueError:
        logging.debug("response body decode error: %s" % resp.text)
        ret = {}
    return ret, ResponseInfo(resp)


def _init():
    global _session
    if _session is None:
        _session = qn_http_client.session

    adapter = HTTPAdapter(
        pool_connections=config.get_default('connection_pool'),
        pool_maxsize=config.get_default('connection_pool'),
        max_retries=config.get_default('connection_retries'))
    _session.mount('http://', adapter)


def _post(url, data, headers=None):
    if _session is None:
        _init()
    try:
        post_headers = _headers.copy()
        if headers is not None:
            for k, v in headers.items():
                post_headers.update({k: v})
        r = _session.post(
            url, json=data, headers=post_headers,
            timeout=config.get_default('connection_timeout'))
    except Exception as e:
        return None, ResponseInfo(None, e)
    return __return_wrapper(r)


def _put(url, data, headers=None):
    if _session is None:
        _init()
    try:
        post_headers = _headers.copy()
        if headers is not None:
            for k, v in headers.items():
                post_headers.update({k: v})
        r = _session.put(
            url, data=data, headers=post_headers,
            timeout=config.get_default('connection_timeout'))
    except Exception as e:
        return None, ResponseInfo(None, e)
    return __return_wrapper(r)


def _get(url, params, auth, headers=None):
    if _session is None:
        _init()
    try:
        get_headers = _headers.copy()
        if headers is not None:
            for k, v in headers.items():
                get_headers.update({k: v})
        r = _session.get(
            url,
            params=params,
            auth=auth,
            timeout=config.get_default('connection_timeout'),
            headers=get_headers)
    except Exception as e:
        return None, ResponseInfo(None, e)
    return __return_wrapper(r)