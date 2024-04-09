# -*- coding: utf-8 -*-
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


class Auth(object):
    """安全机制类

    该类主要内容是凭证的签名接口的实现，以及回调验证。

    Attributes:
        __supplier_no: 供应商编号，双方协商获得
        __private_key: RSA私匙，公钥交给SparkProxy，调用接口时使用私钥签名，sparkproxy使用公钥验签
    """

    def __init__(self, supplier_no, private_key, disable_timestamp_signature=None):
        """初始化Auth类"""
        self.__checkKey(supplier_no, private_key)
        self.__supplier_no = supplier_no
        self.__private_key = self.__load_rsa_private_key(private_key)
        self.disable_timestamp_signature = disable_timestamp_signature

    @staticmethod
    def __load_rsa_private_key(private_key):
        private_key = serialization.load_pem_private_key(
            private_key.encode(),
            password=None,
            backend=default_backend()
        )
        return private_key

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
        signature = self.__private_key.sign(
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return signature.hex()

    @staticmethod
    def __checkKey(access_key, secret_key):
        if not (access_key and secret_key):
            raise ValueError('invalid key')

    def verify_callback(
            self,
            origin_authorization,
            url,
            body,
            content_type='application/x-www-form-urlencoded'):
        """回调验证

        Args:
            origin_authorization: 回调时请求Header中的Authorization字段
            url:                  回调请求的url
            body:                 回调请求的body
            content_type:         回调请求body的Content-Type

        Returns:
            返回true表示验证成功，返回false表示验证失败
        """
        token = self.token_of_request(url, body, content_type)
        authorization = 'QBox {0}'.format(token)
        return origin_authorization == authorization
