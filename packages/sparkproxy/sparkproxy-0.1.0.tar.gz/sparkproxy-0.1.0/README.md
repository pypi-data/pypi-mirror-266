# Qiniu Cloud SDK for Python

[![Software License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/tag/qiniu/python-sdk.svg?label=release)](https://github.com/yungoo/spark-proxy/sdk/spark-sdk-python/releases)
[![Latest Stable Version](https://img.shields.io/pypi/v/sparkproxy.svg)](https://pypi.python.org/pypi/spark-proxy)
[![Download Times](https://img.shields.io/pypi/dm/sparkproxy.svg)](https://pypi.python.org/pypi/spark-proxy)

## 安装

通过pip

```bash
$ pip install sparkproxy
```

## 运行环境

| sparkproxy SDK版本 |              Python 版本               |
|:----------------:| :------------------------------------: |
|       1.x        | 2.7, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9 |

## 使用方法

### 上传
```python
from sparkproxy import Auth
from sparkproxy import SparkProxyClient

...
supplier_no = 'test0001'
with open("key.pem", 'rb') as pem_file:
    private_key = pem_file.read().decode("utf-8")
client = SparkProxyClient(Auth(supplier_no=supplier_no, private_key=private_key))

ret, info = client.get_product_stock(proxy_type=103)
if ret is not None:
    print('All is OK')
else:
    print(info) # error message in info
...

```

```

## 测试

``` bash
$ py.test
```

## 常见问题

- 第二个参数info保留了请求响应的信息，失败情况下ret 为none, 将info可以打印出来，提交给我们。
- API 的使用 demo 可以参考 [examples示例](https://github.com/yungoo/spark-proxy/sdk/spark-sdk-python/tree/master/examples)。
- 如果碰到`ImportError: No module named requests.auth` 请安装 `requests` 。
