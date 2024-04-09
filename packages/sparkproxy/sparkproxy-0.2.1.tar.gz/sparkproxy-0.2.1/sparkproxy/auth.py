# -*- coding: utf-8 -*-
import time

from cryptography.exceptions import InvalidSignature

from sparkproxy.rsa import rsa_load_pem_private_key, rsa_sign, rsa_decrypt, rsa_verify, rsa_load_pem_public_key


class Auth(object):
    """安全机制类

    该类主要内容是凭证的签名接口的实现，以及回调验证。

    Attributes:
        __supplier_no: 供应商编号，双方协商获得
        __private_key: RSA私匙，公钥交给SparkProxy，调用接口时使用私钥签名，sparkproxy使用公钥验签
        __public_key: RSA公钥，SparkProxy提供的公钥
    """

    def __init__(self, supplier_no, private_key, public_key = None):
        """初始化Auth类"""
        self.__checkKey(supplier_no, private_key)
        self.__supplier_no = supplier_no
        self.__private_key = rsa_load_pem_private_key(private_key)
        if public_key is not None:
            self.__public_key = rsa_load_pem_public_key(public_key)

    def get_supplier_no(self):
        return self.__supplier_no

    def get_private_key(self):
        return self.__private_key

    def token_of_request(self, req):
        """带请求体的签名（本质上是管理凭证的签名）

        Args:
            req:         待签名请求的参数
        Returns:
            签名凭证
        """
        message = 'supplierNo={0}&timestamp={1}'.format(req["supplierNo"], req["timestamp"])

        # 使用私钥对哈希值进行签名
        return rsa_sign(message, self.__private_key)

    @staticmethod
    def __checkKey(access_key, secret_key):
        if not (access_key and secret_key):
            raise ValueError('invalid key')

    def decrypt(self, encrypt_msg):
        return rsa_decrypt(encrypt_msg, self.__private_key)

    def verify_callback(
            self,
            supplier_no, sign, req_id, timestamp):
        """回调验证

        Args:
            supplier_no:        回调请求中供应商NO
            sign:              回调请求的签名
            req_id:            回调请求的请求ID
            timestamp:         回调请求的时间戳

        Returns:
            返回ValueError异常表示验证失败
        """
        if not supplier_no:
            raise ValueError(f"签名参数supplierNo未提供。reqId: {req_id}")
        if not sign:
            raise ValueError(f"签名参数sign未提供。reqId: {req_id}")

        if time.time() - timestamp > 600:
            raise ValueError(f"签名已过期。reqId: {req_id}")

        str_to_sign = f"supplierNo={supplier_no}&timestamp={timestamp}"

        try:
            rsa_verify(sign, str_to_sign, self.__public_key)
        except InvalidSignature:
            raise ValueError(f"签名校验错误。reqId: {req_id}")
        except Exception as e:
            raise ValueError(f"签名验证过程中出现问题: {e}")
