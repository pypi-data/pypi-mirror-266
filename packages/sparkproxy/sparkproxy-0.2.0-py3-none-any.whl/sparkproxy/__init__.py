# -*- coding: utf-8 -*-
'''
Qiniu Resource Storage SDK for Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For detailed document, please see:
<https://developer.qiniu.com/kodo/sdk/1242/python>
'''

# flake8: noqa

__version__ = '0.2.0'

from .auth import Auth

from .config import set_default

from .services.openapi.client import SparkProxyClient
