#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Time: 2024-04-01 09:11:56
from __future__ import annotations

import base64
import binascii
import os.path
from typing import Tuple

import click
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from easy_encryption_tool import random_str


def decode_b64_data(data: str) -> bytes:
    if len(data) <= 0:
        return bytes()
    try:
        # 尝试解码Base64字符串
        decoded_bytes = base64.b64decode(data)
        return decoded_bytes
    except binascii.Error as e:
        raise e


def check_is_file_readable(input_data: str) -> bool:
    """检查文件是否存在以及是否可读"""
    return os.path.exists(input_data) and os.access(input_data, mode = os.R_OK) and os.path.isfile(input_data)


def check_is_file_writable(input_data: str) -> bool:
    """
        如果文件不存在则创建
        如果文件存在且文件类型是文件（非目录）且文件可写，则清空
        如果文件存在且不可写则报错
    """
    if not os.path.exists(input_data) or (os.path.isfile(input_data) and os.access(input_data, os.W_OK)):
        with open(input_data, 'w') as file:
            file.truncate(0)
            return True
    return False


def check_b64_data(input_data: str) -> Tuple[bool, bytes]:
    if len(input_data) <= 0:
        return False, b''
    try:
        ret = decode_b64_data(input_data)
    except binascii.Error:
        return False, b''
    else:
        if len(ret) <= 0:
            return False, b''
        return True, ret


class read_from_file(object):
    """
    读取指定的文件
    """

    def __init__(self, file_path: str):
        self.__opened = False
        if not check_is_file_readable(file_path):
            raise Exception('read from file {} error'.format(file_path))
        self.__file = open(file_path, 'rb')
        self.__path = file_path
        self.__opened = True
        # click.echo('{} opened in mode rb success'.format(file_path))

    def read_n_bytes(self, n: int) -> bytes:
        return self.__file.read(n)

    # def close(self):
    #     self.__file.close()

    def __del__(self):  # 调用方不能主动关闭文件
        if self.__opened:
            self.__file.close()
            # click.echo('{} closed success'.format(self.__path))


class write_to_file(object):
    def __init__(self, file_path: str):
        self.__opened = False
        if not check_is_file_writable(file_path):
            raise Exception('write to file {} error'.format(file_path))
        self.__file = open(file_path, 'wb')
        self.__path = file_path
        self.__opened = True
        # click.echo('{} opened in mode wb success'.format(file_path))

    def write_bytes(self, data: bytes) -> bool:
        try:
            if len(data) > 0:
                self.__file.write(data)
                self.__file.flush()
        except BaseException as e:  # 预防磁盘写满等异常情况，不够这种情况概率比较小
            click.echo('write to {} failed\n{}\n'.format(self.__path, e))
            return False
        else:
            return True

    # def close_file(self):
    #     self.__file.close()

    def __del__(self):  # 调用方不能主动关闭文件
        if self.__opened:
            self.__file.close()
            # click.echo('{} closed success'.format(self.__path))


encoding_maps = {
    'pem': serialization.Encoding.PEM,
    'der': serialization.Encoding.DER,
    # 'ssh': serialization.Encoding.OpenSSH,
    # 'raw': serialization.Encoding.Raw,
    # 'smime': serialization.Encoding.SMIME,
    # 'x962': serialization.Encoding.X962,
}


def private_key_password(is_random: bool, password: str | None):
    enc = serialization.NoEncryption()
    if is_random:
        password = random_str.generate_random_str(32)
    if password is not None and len(password) > 0:  # 如果传入了密码，则在生成私钥文件时需要对私钥做加密
        enc = serialization.BestAvailableEncryption(password.encode('utf-8'))
    return password, enc


def load_public_key(encoding: str, file_path: str):
    try:
        pub_key = None
        with open(file_path, 'rb') as key_file:
            if encoding == 'pem':
                pub_key = serialization.load_pem_public_key(key_file.read(), backend = default_backend())
            if encoding == 'der':
                pub_key = serialization.load_der_public_key(key_file.read(), backend = default_backend())
    except BaseException as e:
        click.echo('load public key:{} failed\nERROR:{}'.format(file_path, e))
        return None
    else:
        return pub_key


def load_private_key(encoding: str, file_path: str, password_bytes: bytes):
    pri_key = None
    try:  # 读取私钥
        with open(file_path, 'rb') as key_file:
            if encoding == 'pem':
                pri_key = serialization.load_pem_private_key(key_file.read(),
                                                             backend = default_backend(),
                                                             password = password_bytes)
            if encoding == 'der':
                pri_key = serialization.load_der_private_key(key_file.read(),
                                                             backend = default_backend(),
                                                             password = password_bytes)
    except BaseException as e:
        click.echo('load private key:{} failed:{}'.format(file_path, e))
        return None
    else:
        return pri_key


def bytes_to_str(data: bytes) -> Tuple[bool, str]:
    try:
        ret = data.decode('utf-8')
    except BaseException:
        return False, base64.b64encode(data).decode('utf-8')
    else:
        return True, ret


def write_asymmetric_key(file_name_prefix: str, asymmetric_type: str,
                         encoding_type: str, is_private_encrypted: bool,
                         private_password: str,
                         public_data: bytes, private_data: bytes) -> bool:
    if file_name_prefix is None or len(file_name_prefix) <= 0:
        return False

    if len(file_name_prefix) > 0:
        public_file = '{}_{}_public.{}'.format(file_name_prefix, asymmetric_type, encoding_type)
        private_file = '{}_{}_private.{}'.format(file_name_prefix, asymmetric_type, encoding_type)
        if is_private_encrypted and private_password is not None and len(private_password) > 0:
            private_file = '{}_{}_private_cipher.{}'.format(file_name_prefix, asymmetric_type, encoding_type)
        for i in [public_file, private_file]:
            try:
                f = write_to_file(i)
            except BaseException as e:
                click.echo('write to {} failed:{}'.format(i, e))
                return False
            else:
                if i == public_file:
                    if not f.write_bytes(public_data):
                        return False
                elif i == private_file:
                    if not f.write_bytes(private_data):
                        return False
                    if is_private_encrypted and private_password is not None and len(private_password) > 0:
                        click.echo('private key password:{}'.format(private_password))
        click.echo('generate {}/{} success'.format(public_file, private_file))
        return True
