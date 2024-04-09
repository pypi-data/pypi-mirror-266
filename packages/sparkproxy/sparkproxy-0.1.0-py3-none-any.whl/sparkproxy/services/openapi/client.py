# -*- coding: utf-8 -*-
import time
import uuid

from sparkproxy import config
from sparkproxy import http


class SparkProxyClient(object):
    """资源管理客户端

    使用应用密钥生成资源管理客户端，可以进一步：
    1、部署服务和容器，获得信息
    2、创建网络资源，获得信息

    属性：
        auth: 应用密钥对，Auth对象
        host: API host

    接口：
        get_product_stock(args)
        create_proxy(args)
        renew_proxy(args)
        delete_proxy(stack)
        get_order(stack)
        get_instance(stack)
    """

    def __init__(self, auth, host=None):
        self.auth = auth
        if host is None:
            self.host = config.get_default("default_api_host")
        else:
            self.host = host

    def get_product_stock(self, proxy_type, country_code = None, city_code = None):
        """获取商品库存

        列出当前所有在售的商品及其库存信息。

        Returns:
            返回一个tuple对象，其格式为(<result>, <ResponseInfo>)
            - result          成功返回服务组列表[<product1>, <product1>, ...]，失败返回{"error": "<errMsg string>"}
            - ResponseInfo    请求的Response信息
        """
        return self.__post('GetProductStock', {"proxyType": proxy_type, "countryCode": country_code, "cityCode": city_code})

    def create_proxy(self, req_order_no, sku, amount, duration, unit, country_code, city_code):
        """创建代理实例

        创建新代理实例，返回订单信息

        Args:
            - req_order_no: 请求方订单ID
            - sku:  商品ID
            - amount: IP数量
            - duration: 必要 时长 0无限制
            - unit: 单位 1 天;2 周（7天）;3 月(自然月; 4年(自然年365，366）
            - country_code: 必要,国家代码 3位 iso标准
            - city_code: 必要,城市代码 向我方提取

        Returns:
            返回一个tuple对象，其格式为(<result>, <ResponseInfo>)
            - result          成功返回空dict{}，失败返回{"error": "<errMsg string>"}
            - ResponseInfo    请求的Response信息
        """
        return self.__post('CreateProxy', {"reqOrderNo": req_order_no, "sku": sku, "amount": amount,
                                           "duration": duration, "unit": unit, "countryCode": country_code, "cityCode": city_code})

    def renew_proxy(self, req_order_no, instances):
        """续费代理实例

        续费新代理实例，返回新订单信息

        Args:
            - args:  订单&实例描述

        Returns:
            返回一个tuple对象，其格式为(<result>, <ResponseInfo>)
            - result          成功返回空dict{}，失败返回{"error": "<errMsg string>"}
            - ResponseInfo    请求的Response信息
        """
        return self.__post('RenewProxy', {"reqOrderNo": req_order_no, "instances": instances})

    def delete_proxy(self, req_order_no, instances):
        """删除代理实例

        删除代理实例，删除即时生效

        Args:
            - args:  实例描述

        Returns:
            返回一个tuple对象，其格式为(<result>, <ResponseInfo>)
            - result          成功返回空dict{}，失败返回{"error": "<errMsg string>"}
            - ResponseInfo    请求的Response信息
        """
        return self.__post('DelProxy', {"reqOrderNo": req_order_no, "instanceIds": instances})

    def get_order(self, req_order_no):
        """获取订单信息

        获取订单信息

        Args:
            - req_order_no:  请求方订单ID

        Returns:
            返回一个tuple对象，其格式为(<result>, <ResponseInfo>)
            - result          成功返回空dict{}，失败返回{"error": "<errMsg string>"}
            - ResponseInfo    请求的Response信息
        """
        return self.__post('GetOrder', {"reqOrderNo": req_order_no})

    def get_instance(self, instance_id):
        """获取订单信息

        获取订单信息

        Args:
            - instance_id:  实例ID

        Returns:
            返回一个tuple对象，其格式为(<result>, <ResponseInfo>)
            - result          成功返回空dict{}，失败返回{"error": "<errMsg string>"}
            - ResponseInfo    请求的Response信息
        """
        return self.__post('GetInstance', {"instanceId": instance_id})

    def __request_params(self, method, args):
        base_params = {
            "method": method,
            "version": "2024-04-08",
            "reqId": str(uuid.uuid4()),
            "timestamp": int(time.time()),
            "supplierNo": self.auth.get_supplier_no(),
            "sign": "",
            "params": args
        }
        base_params["sign"] = self.auth.token_of_request(base_params)
        return base_params

    def __post(self, method, data=None):
        url = '{0}/v1/open/api'.format(self.host)
        req = self.__request_params(method, data)
        return http._post(url, req)
