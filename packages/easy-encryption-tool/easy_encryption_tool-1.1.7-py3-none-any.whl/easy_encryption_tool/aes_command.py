#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Time: 2024-03-30 15:53:00
from __future__ import annotations

import base64
import json
import os
from typing import Tuple

import click
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

from easy_encryption_tool import common
from easy_encryption_tool import random_str
from easy_encryption_tool import command_perf

algorithm: str = 'aes'

aes_block_in_bytes = algorithms.AES.block_size // 8

aes_key_len_256: int = 32  # 32字节
aes_iv_len_128: int = 16  # 16字节
aes_nonce_len_128: int = 12  # 12字节

aes_cbc_mode: str = 'cbc'
aes_gcm_mode: str = 'gcm'

aes_encrypt_action = 'encrypt'
aes_decrypt_action = 'decrypt'

aes_gcm_tag_len = aes_block_in_bytes

aes_file_read_block = aes_block_in_bytes


def generate_random_key() -> str:
    return random_str.generate_random_str(aes_key_len_256)


def generate_random_iv_nonce(mode: str) -> str:
    if mode == aes_cbc_mode:
        return random_str.generate_random_str(aes_iv_len_128)
    elif mode == aes_gcm_mode:
        return random_str.generate_random_str(aes_nonce_len_128)


def process_key_iv(is_random: bool, key: str, iv: str, mode: str) -> Tuple[str, str]:
    # 如果需要随机产生 key 和 iv/nonce 数据
    if is_random:
        return generate_random_key(), generate_random_iv_nonce(mode)
    else:  # 如果不需要随机产生，则检查密钥和 iv 的长度并做填充
        key_len = len(key)
        if key_len > aes_key_len_256:
            key = key[:aes_key_len_256]
        else:
            key = key + random_str.generate_random_str(aes_key_len_256 - key_len)
        if mode == aes_cbc_mode:
            if len(iv) > aes_iv_len_128:
                iv = iv[:aes_iv_len_128]
            elif len(iv) < aes_iv_len_128:
                iv = iv + random_str.generate_random_str(aes_iv_len_128 - len(iv))
        elif mode == aes_gcm_mode:
            if len(iv) > aes_nonce_len_128:
                iv = iv[:aes_nonce_len_128]
            elif len(iv) < aes_nonce_len_128:
                iv = iv + random_str.generate_random_str(aes_nonce_len_128 - len(iv))
        return key, iv


def padding_data(data: bytes) -> bytes:
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    return padded_data


def remove_padding_data(data: bytes) -> bytes:
    # 对于空字节流，这里不做任何处理，直接返回空
    if data is None or len(data) == 0:
        return b''
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(data) + unpadder.finalize()
    return decrypted_data


class aes_operator(object):
    def __init__(self, mode: str, action: str, key: bytes, iv: bytes, tags: bytes):
        """
        :param mode: cbc 或 gcm
        :param action: encrypt 或 decrypt
        :param key: 32字节
        :param iv:  16字节
        :param tags:  gcm 模式解密时需要传入
        """
        self.__mode = mode
        self.__action = action
        self.__tags = tags
        self.__key = key
        self.__iv = iv
        if mode == aes_cbc_mode:
            self.__aes_cbc_obj = Cipher(algorithms.AES(self.__key), modes.CBC(self.__iv), backend = default_backend())
            if action == aes_encrypt_action:
                self.__aes_cbc_enc_op = self.__aes_cbc_obj.encryptor()
            if action == aes_decrypt_action:
                self.__aes_cbc_dec_op = self.__aes_cbc_obj.decryptor()
        if mode == aes_gcm_mode:
            self.__auth_data = json.dumps({
                'mode': mode,
                'obj': 'aes_operator',
            }).encode(encoding = 'utf-8')
            if action == aes_encrypt_action:
                self.__aes_gcm_obj = Cipher(algorithms.AES(self.__key), modes.GCM(self.__iv), backend = default_backend())
                self.__aes_gcm_enc_op = self.__aes_gcm_obj.encryptor()
                self.__aes_gcm_enc_op.authenticate_additional_data(self.__auth_data)
            if action == aes_decrypt_action:
                self.__aes_gcm_obj = Cipher(algorithms.AES(self.__key), modes.GCM(self.__iv, self.__tags),
                                            backend = default_backend())
                self.__aes_gcm_dec_op = self.__aes_gcm_obj.decryptor()
                self.__aes_gcm_dec_op.authenticate_additional_data(self.__auth_data)

    def process_data(self, data: bytes) -> bytes:
        if self.__mode == aes_cbc_mode:
            if self.__action == aes_encrypt_action:
                return self.__aes_cbc_enc_op.update(data)
            if self.__action == aes_decrypt_action:
                return self.__aes_cbc_dec_op.update(data)
        if self.__mode == aes_gcm_mode:
            if self.__action == aes_encrypt_action:
                return self.__aes_gcm_enc_op.update(data)
            if self.__action == aes_decrypt_action:
                return self.__aes_gcm_dec_op.update(data)

    def finalize(self) -> Tuple[bytes, bytes]:
        """
        gcm模式加密时返回密文和 tag
        gcm模式解密时需要传入 tag
        """
        if self.__mode == aes_cbc_mode:
            if self.__action == aes_encrypt_action:
                return self.__aes_cbc_enc_op.finalize(), b''
            if self.__action == aes_decrypt_action:
                return self.__aes_cbc_dec_op.finalize(), b''
        if self.__mode == aes_gcm_mode:
            if self.__action == aes_encrypt_action:
                return self.__aes_gcm_enc_op.finalize(), self.__aes_gcm_enc_op.tag
            if self.__action == aes_decrypt_action:
                return self.__aes_gcm_dec_op.finalize_with_tag(self.__tags), b''

    @property
    def mode(self) -> str:
        return self.__mode

    @property
    def action(self) -> str:
        return self.__action

    @property
    def key(self) -> bytes:
        return self.__key

    @property
    def iv_nonce(self) -> bytes:
        return self.__iv


def check_gcm_tag(gcm_tag: str) -> bool:
    if gcm_tag is None:
        click.echo('expected a gcm tag(16 Bytes)')
        return False
    valid, input_raw_tag = common.check_b64_data(gcm_tag)
    if not valid:
        click.echo('invalid b64 encoded tag data:{}'.format(gcm_tag))
        return False
    if len(input_raw_tag) != aes_gcm_tag_len:
        click.echo('invalid tag data length:{}, expected:{}'.format(len(input_raw_tag), aes_gcm_tag_len))
        return False
    return True


def check_b64_input_data(input_data: str, input_limit: int) -> bool:
    if input_data is None:
        click.echo('need input data')
        return False
    valid, input_raw_bytes = common.check_b64_data(input_data)
    if not valid:
        click.echo('invalid b64 encoded data:{}'.format(input_data))
        return False
    if len(input_raw_bytes) > input_limit * 1024 * 1024:
        click.echo(
            'the data exceeds the maximum bytes limit, limited to:{}Bytes, now:{}Bytes'.format(input_limit * 1024 * 1024,
                                                                                               len(input_raw_bytes)))
        return False
    if len(input_raw_bytes) <= 0:
        click.echo('need plain data but now got empty after base64 decoded')
        return False
    return True


@click.command(name = 'aes', short_help = 'aes加解密工具，默认支持 aes-cbc-256 和 aes-gcm-256')
@click.option('-m', '--mode',
              required = False,
              type = click.Choice([aes_cbc_mode, aes_gcm_mode]),
              default = 'cbc',
              show_default = True,
              help = 'aes mode，默认为 cbc 模式，可选 cbc 或 gcm 模式',
              is_flag = False,
              multiple = False)
@click.option('-k', '--key',
              required = False,
              type = click.STRING,
              default = 'k' * 32,
              help = 'key 默认 32 字节，即 256 位，'
                     '只允许输入可见字符, 长度不够则自动补齐，长度超出则自动截取',
              show_default = True,
              is_flag = False,
              multiple = False)
@click.option('-v', '--iv-nonce',
              required = False,
              type = click.STRING,
              default = 'v' * 16,
              help = ' cbc 模式下，iv 默认 16 字节即 128 位，gcm 模式下 nonce 默认 12 字节即 96 位，'
                     '长度不够则自动补齐，长度超出则自动截取',
              show_default = True,
              is_flag = False,
              multiple = False)
@click.option('-r', '--random-key-iv',
              required = False,
              type = click.BOOL,
              is_flag = True,
              default = False,
              help = '是否自动生成随机的密钥和 iv/nonce，如果随机生成，则密钥长度默认 32 字节，iv 默认为 16 字节， nonce 默认为 12 字节',
              multiple = False)
@click.option('-a', '--action',
              required = False,
              type = click.Choice([aes_encrypt_action, aes_decrypt_action]),
              default = 'encrypt',
              show_default = True,
              help = '加密（encrypt）或 解密（decrypt），加密后输出 base64 编码的字符串',
              is_flag = False,
              multiple = False)
@click.option('-i', '--input-data',
              required = True,
              type = click.STRING,
              help = '输入数据，即被加密或解密的数据，加密时允许输入：字符串、 base64 编码数据、文件路径，解密时允许输入：base64 编码数据、文件路径')
@click.option('-e', '--is-base64-encoded',
              required = False,
              type = click.BOOL,
              is_flag = True,
              default = False,
              show_default = True,
              help = '如果 -i/--input-data 的值被 base64 编码过，则需要带上 -e 参数，-e 与 -f 互斥')
@click.option('-f', '--is-a-file',
              required = False,
              type = click.BOOL,
              is_flag = True,
              default = False,
              show_default = False,
              help = '如果 -i/--input-data 的值是一个文件，则需要带上 -f 参数表示当前需要被处理的是一个文件，-e 与 -f 互斥')
@click.option('-l', '--input-limit',
              required = False,
              type = click.INT,
              default = 1,
              show_default = True,
              help = '输入内容最大长度，单位为 MB，默认为 1MB，在 -i 为非文件时生效')
@click.option('-o', '--output-file',
              required = False,
              type = click.STRING,
              default = '',
              help = '指定输出文件，当输入时指定了文件，则输出时必须指定')
@click.option('-t', '--gcm-tag',
              required = False,
              type = click.STRING,
              help = 'gcm 模式解密时，则此参数必填')
@command_perf.timing_decorator
def aes_command(mode: click.STRING, key: click.STRING, iv_nonce: click.STRING,
                random_key_iv: click.BOOL, action: click.STRING,
                input_data: click.STRING, is_base64_encoded: click.BOOL,
                is_a_file: click.BOOL, input_limit: click.INT,
                output_file: click.STRING, gcm_tag: click.STRING):
    """
        加密：
            对明文加密
            对 base64 的字节流加密
            对文件加密
                密文输出到 stdout
                密文输出到 stdout 且写入到指定文件
        解密：
            对 base64 的字符串解密
            对文件解密
                明文是字符串
                明文是字节流
                    明文输出到 stdout
                    明文输出到 stdout 且写入到指定文件
    """

    # 预处理 key 和 iv/nonce
    key, iv_nonce = process_key_iv(random_key_iv, key, iv_nonce, mode)

    # 检查输入数据
    if len(input_data) <= 0:
        click.echo('no input data, it is required')
        return

    # 输入不能同时作为文件和 base64数据
    if is_base64_encoded and is_a_file:
        click.echo('the input data cannot be used as both a file and base64 encoded data')
        return

    input_raw_bytes = b''
    input_raw_tag = b''

    # gcm模式下解密，需要对输入的 gcm_tag 做检查拿到真实的 tag 字节流
    if mode == aes_gcm_mode and action == aes_decrypt_action:
        if not check_gcm_tag(gcm_tag):
            return
        input_raw_tag = common.decode_b64_data(gcm_tag)

    # 如果输入被 base64 编码过
    if is_base64_encoded:
        if not check_b64_input_data(input_data, input_limit):
            return
        input_raw_bytes = common.decode_b64_data(input_data)

    input_from_file = None
    output_to_file = None
    # 如果输入是文件
    if is_a_file:
        try:
            input_from_file = common.read_from_file(input_data)
        except BaseException:
            click.echo('{} may not exist or may be unreadable'.format(input_data))
            return
        else:
            # 如果加密一个文件或解密一个文件，则必须指定输出的文件
            if len(output_file) <= 0:
                click.echo('need a output file specified and writable')
                return

    # 如果输入既不是文件也不是 base64 编码的数据
    if not is_base64_encoded and not is_a_file:  # 既没有被编码也不是文件，就是字符串作为明文
        if len(input_data) > input_limit * 1024 * 1024:
            click.echo(
                'the data exceeds the maximum bytes limit, limited to:{}Bytes, now:{}Bytes'.format(input_limit * 1024 * 1024,
                                                                                                   len(input_data)))
            return
        input_raw_bytes = input_data.encode('utf-8')

    # 如果指定了输出文件
    if len(output_file) > 0:
        try:
            output_to_file = common.write_to_file(output_file)
        except BaseException:
            click.echo('{} may not exist or may not writable'.format(output_file))
            return

    # 如果是命令行参数解密，则需要输入 gcm_tag
    aes_op = aes_operator(mode = mode, action = action,
                          key = key.encode('utf-8'),
                          iv = iv_nonce.encode('utf-8'),
                          tags = input_raw_tag)

    # 如果输入不是一个文件
    if not is_a_file and input_from_file is None:
        if action == aes_encrypt_action:
            # 加密数据，直接对原始数据做 padding
            padded_raw_bytes = padding_data(input_raw_bytes)
            cipher = aes_op.process_data(padded_raw_bytes)
            cipher_last_block, ret_tags = aes_op.finalize()
            all_cipher = cipher + cipher_last_block
            all_cipher_str = base64.b64encode(all_cipher).decode('utf-8')
            tag_str = base64.b64encode(ret_tags).decode('utf-8')
            click.echo(
                'plain size:{}\nkey:{}\niv:{}\ncipher size:{}\ncipher:{}\nauth_tag_size:{}\nauth_tag:{}'.format(
                    len(input_raw_bytes),
                    key, iv_nonce,
                    len(all_cipher),
                    all_cipher_str,
                    len(ret_tags),
                    tag_str))
            if output_to_file is not None and not output_to_file.write_bytes(all_cipher):
                return
        if action == aes_decrypt_action:
            try:
                plain = aes_op.process_data(input_raw_bytes)
                plain_last_block, ret_tags = aes_op.finalize()
                origin_plain = remove_padding_data(plain + plain_last_block)
            except BaseException as e:  # 如果解密失败的话
                click.echo('decrypt {} failed:{}'.format(input_data, e))
                return
            else:  # 如果解密成功，则判断明文能否被 utf-8 解码，如果可以解码则直接打印，否则 base64 编码后打印
                be_str, ret = common.bytes_to_str(origin_plain)
                if be_str:
                    click.echo('cipher size:{}\nplain size:{}\nstr plain:{}'.format(
                        len(input_raw_bytes),
                        len(origin_plain), ret))
                else:
                    click.echo('cipher size:{}\nplain size:{}\nb64 encoded plain:{}'.format(
                        len(input_raw_bytes),
                        len(origin_plain), ret))
                if output_to_file is not None and not output_to_file.write_bytes(origin_plain):
                    return

    # 如果输入是对文件操作，那么输出一定是个文件
    if is_a_file and input_from_file is not None and output_to_file is not None:
        read_size = (aes_file_read_block ** 5) * 64  # 每次读取 64MB
        file_size = os.stat(input_data).st_size
        output_size = 0
        click.echo('input file size:{}'.format(file_size))
        if action == aes_encrypt_action:  # 对文件加密，密文写入指定文件中
            while True:
                chunk = input_from_file.read_n_bytes(read_size)
                file_size -= len(chunk)
                if file_size <= 0:  # 读到文件末尾了
                    # 最后一个 block 一定要做一次 padding
                    # 否则解密的时候无法判断是否需要去除 padding
                    chunk = padding_data(chunk)
                    cipher = aes_op.process_data(chunk)
                    output_size += len(cipher)
                    if not output_to_file.write_bytes(cipher):
                        return
                    cipher_last_block, tag = aes_op.finalize()
                    output_size += len(cipher_last_block)
                    if not output_to_file.write_bytes(cipher_last_block):
                        return
                    click.echo('cipher size:{}\nkey:{}\niv:{}\nauth_tag_size:{}\nauth_tag:{}'.format(
                        output_size,
                        key, iv_nonce,
                        len(tag),
                        base64.b64encode(tag).decode('utf-8')))
                    break
                cipher = aes_op.process_data(chunk)
                output_size += len(cipher)
                if not output_to_file.write_bytes(cipher):
                    return
        if action == aes_decrypt_action:
            if file_size < aes_file_read_block or file_size % aes_file_read_block != 0:
                click.echo('invalid cipher file size:{} Bytes'.format(file_size))
                return
            try:
                # 对密文解密，明文写入指定文件中
                while True:
                    """
                    解密最后一个密文块，并将其保存在内存中。
                    在内存中对最后一个解密后的明文块执行PKCS#7去填充操作
                    """
                    chunk = input_from_file.read_n_bytes(read_size)
                    file_size -= len(chunk)
                    plain = aes_op.process_data(chunk)
                    if file_size == 0:  # 文件已经读完了
                        plain = remove_padding_data(plain)
                        output_size += len(plain)
                        if not output_to_file.write_bytes(plain):
                            return
                        click.echo('decrypt {} success\nwrite to {}\nplain size:{}'.format(input_data, output_file, output_size))
                        return
                    output_size += len(plain)
                    if not output_to_file.write_bytes(plain):
                        return

            except BaseException as e:
                click.echo('decrypt {} failed:{}'.format(input_data, e))
                return


if __name__ == '__main__':
    aes_command()
