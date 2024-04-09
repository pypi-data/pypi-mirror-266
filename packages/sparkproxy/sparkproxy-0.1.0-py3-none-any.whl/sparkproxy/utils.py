# -*- coding: utf-8 -*-
from hashlib import sha1, new as hashlib_new
from base64 import urlsafe_b64encode, urlsafe_b64decode
from datetime import datetime
from .compat import b, s

try:
    import zlib

    binascii = zlib
except ImportError:
    zlib = None
    import binascii

_BLOCK_SIZE = 1024 * 1024 * 4


def urlsafe_base64_encode(data):
    """urlsafe的base64编码:

    对提供的数据进行urlsafe的base64编码。规格参考：
    https://developer.qiniu.com/kodo/manual/1231/appendix#1

    Args:
        data: 待编码的数据，一般为字符串

    Returns:
        编码后的字符串
    """
    ret = urlsafe_b64encode(b(data))
    return s(ret)


def urlsafe_base64_decode(data):
    """urlsafe的base64解码:

    对提供的urlsafe的base64编码的数据进行解码

    Args:
        data: 待解码的数据，一般为字符串

    Returns:
        解码后的字符串。
    """
    ret = urlsafe_b64decode(s(data))
    return ret


def io_crc32(io_data):
    result = 0
    for d in io_data:
        result = binascii.crc32(d, result) & 0xFFFFFFFF
    return result


def io_md5(io_data):
    h = hashlib_new('md5')
    for d in io_data:
        h.update(d)
    return h.hexdigest()


def crc32(data):
    """计算输入流的crc32检验码:

    Args:
        data: 待计算校验码的字符流

    Returns:
        输入流的crc32校验码。
    """
    return binascii.crc32(b(data)) & 0xffffffff


def _sha1(data):
    """单块计算hash:

    Args:
        data: 待计算hash的数据

    Returns:
        输入数据计算的hash值
    """
    h = sha1()
    h.update(data)
    return h.digest()


def decode_entry(e):
    return (s(urlsafe_base64_decode(e)).split(':') + [None] * 2)[:2]


def rfc_from_timestamp(timestamp):
    """将时间戳转换为HTTP RFC格式

    Args:
        timestamp: 整型Unix时间戳（单位秒）
    """
    last_modified_date = datetime.utcfromtimestamp(timestamp)
    last_modified_str = last_modified_date.strftime(
        '%a, %d %b %Y %H:%M:%S GMT')
    return last_modified_str


def _valid_header_key_char(ch):
    is_token_table = [
        "!", "#", "$", "%", "&", "\\", "*", "+", "-", ".",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
        "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
        "U", "W", "V", "X", "Y", "Z",
        "^", "_", "`",
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
        "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
        "u", "v", "w", "x", "y", "z",
        "|", "~"]
    return 0 <= ord(ch) < 128 and ch in is_token_table


def canonical_mime_header_key(field_name):
    for ch in field_name:
        if not _valid_header_key_char(ch):
            return field_name
    result = ""
    upper = True
    for ch in field_name:
        if upper and "a" <= ch <= "z":
            result += ch.upper()
        elif not upper and "A" <= ch <= "Z":
            result += ch.lower()
        else:
            result += ch
        upper = ch == "-"
    return result
