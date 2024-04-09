import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import os


def rsa_load_pem_private_key(pri_key):
    private_key = serialization.load_pem_private_key(
        pri_key.encode(),
        password=None,
        backend=default_backend()
    )
    return private_key


def rsa_load_pem_public_key(pub_key):
    public_key = serialization.load_pem_public_key(
        pub_key.encode(),
        backend=None  # Uses the default backend
    )
    return public_key


def rsa_decrypt(encrypted_msg_hex, private_key):
    # 十六进制解码
    encrypted_msg = bytes.fromhex(encrypted_msg_hex)
    
    # 使用PKCS1v15解密
    decrypted_msg = private_key.decrypt(
        encrypted_msg,
        padding.PKCS1v15()
    )
    
    return decrypted_msg


def rsa_sign(message, private_key):
    # 使用私钥对哈希值进行签名
    signature = private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return signature.hex()


def rsa_verify(sign, message, public_key):
    try:
        decoded_sign = base64.b64decode(sign)
    except Exception as e:
        raise ValueError(f"签名解码失败: {e}")

    public_key.verify(
        decoded_sign,
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
