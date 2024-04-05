#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Time: 2024-04-02 10:57:19
import hashlib
import hmac

import click

from easy_encryption_tool import common
from easy_encryption_tool import random_str
from easy_encryption_tool import command_perf

hash_maps = {
    hashlib.sha224().name: hashlib.sha384,
    hashlib.sha256().name: hashlib.sha256,
    hashlib.sha384().name: hashlib.sha384,
    hashlib.sha512().name: hashlib.sha512,
    hashlib.sha3_224().name: hashlib.sha3_224,
    hashlib.sha3_256().name: hashlib.sha3_256,
    hashlib.sha3_384().name: hashlib.sha3_384,
    hashlib.sha3_512().name: hashlib.sha3_512,
}


@click.command(name = 'hmac', short_help = 'hmac消息验证码工具')
@click.option('-i', '--input-data',
              required = True,
              type = click.STRING,
              help = '输入数据，允许输入：字符串、 base64 编码数据、文件路径')
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
@click.option('-h', '--hash-alg',
              required = False,
              type = click.Choice(list(hash_maps.keys())),
              default = hashlib.sha256().name,
              show_default = True,
              help = '哈希算法')
@click.option('-k', '--key',
              required = False,
              type = click.STRING,
              default = 'k' * 32,
              help = 'key 默认值为 32 字节，即 256 位，'
                     '只允许输入可见字符',
              show_default = True,
              is_flag = False,
              multiple = False)
@click.option('-r', '--random-key',
              required = False,
              type = click.BOOL,
              is_flag = True,
              default = False,
              help = '是否自动生成随机的密钥，如果自动生成随机密钥则默认 32 字节长度',
              multiple = False)
@command_perf.timing_decorator
def hmac_command(input_data: click.STRING, is_base64_encoded: click.BOOL,
                 is_a_file: click.BOOL, random_key: click.BOOL, key: click.STRING, hash_alg: click.STRING):
    # 确定密钥内容
    if random_key:
        key = random_str.generate_random_str(32)

    # 生成 hmac 对象
    h = hmac.new(key = key.encode('utf-8'), digestmod = hash_maps[hash_alg])

    if not is_a_file:
        input_raw_bytes = b''
        if not is_base64_encoded:
            input_raw_bytes = input_data.encode('utf-8')
        elif is_base64_encoded:
            try:
                input_raw_bytes = common.decode_b64_data(input_data)
            except BaseException as e:
                click.echo('invalid b64 encoded data:{}'.format(e))
                return
        h.update(input_raw_bytes)
        ret = h.hexdigest()
        click.echo('data size:{}Bytes\nkey:{}\nhmac:{}'.format(len(input_raw_bytes), key, ret))
    else:
        try:
            input_file = common.read_from_file(input_data)
        except BaseException:
            click.echo('file {} may not exists or readable'.format(input_data))
            return
        else:
            data_len = 0
            while True:
                data = input_file.read_n_bytes(32)
                data_len += len(data)
                if len(data) > 0:
                    h.update(data)
                else:
                    ret = h.hexdigest()
                    click.echo('file size:{}Bytes\nkey:{}\nhmac:{}'.format(data_len, key, ret))
                    return


if __name__ == '__main__':
    hmac_command()
