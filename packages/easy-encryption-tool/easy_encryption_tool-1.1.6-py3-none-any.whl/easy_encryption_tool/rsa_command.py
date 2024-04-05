#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Time: 2024-04-02 12:48:05
import base64

import click
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from easy_encryption_tool import command_perf
from easy_encryption_tool import common

rsa_key_size = ['2048', '3072', '4096']
rsa_encryption_mode = ['oaep', 'pkcs1v15']
rsa_sign_mode = ['pss', 'pkcs1v15']

rsa_hash_map = {
    hashes.SHA256().name: hashes.SHA256,
    hashes.SHA384().name: hashes.SHA384,
    hashes.SHA512().name: hashes.SHA512,

    # cryptography库的当前不支持使用SHA3-512哈希算法与OAEP填充模式的组合
    # hashes.SHA3_224().name: hashes.SHA3_224,
    # hashes.SHA3_256().name: hashes.SHA3_256,
    # hashes.SHA3_384().name: hashes.SHA3_384,
    # ashes.SHA3_512().name: hashes.SHA3_512,
}


@click.group(name = 'rsa', short_help = 'rsa加解密和签名验签工具')
def rsa_group():
    pass


@click.command(name = 'generate')
@click.option('-s', '--size',
              type = click.Choice(list(rsa_key_size)),
              required = False,
              default = '2048',
              show_default = True,
              help = '密钥位数')
@click.option('-e', '--encoding',
              type = click.Choice(list(common.encoding_maps.keys())),
              default = 'pem',
              show_default = True,
              help = '密钥格式')
@click.option('-f', '--file-name',
              required = True,
              type = click.STRING,
              default = 'demo',
              show_default = True,
              help = '输出密钥对的文件名前缀，最终写入数据时会创建文件并加上文件名后缀')
@click.option('-p', '--password',
              required = False,
              type = click.STRING,
              help = '私钥密码，使用私钥时需要输入正确的密码')
@click.option('-r', '--random-password',
              required = False,
              type = click.BOOL,
              is_flag = True,
              help = '是否生成私钥的随机密码，如果带上 -r 标识，则随机生成32字节的密码')
@command_perf.timing_decorator
def generate_key_pair(size: click.STRING, encoding: click.STRING, file_name: click.STRING,
                      password: click.STRING, random_password: click.BOOL):
    password, enc = common.private_key_password(random_password, password)

    private_key = rsa.generate_private_key(
        public_exponent = 65537,
        key_size = int(size),
    )
    public_key = private_key.public_key()
    private_encoding = private_key.private_bytes(
        encoding = common.encoding_maps[encoding],
        format = serialization.PrivateFormat.PKCS8,
        encryption_algorithm = enc,
    )
    public_encoding = public_key.public_bytes(
        encoding = common.encoding_maps[encoding],
        format = serialization.PublicFormat.SubjectPublicKeyInfo
    )
    if not common.write_asymmetric_key(file_name_prefix = file_name,
                                       asymmetric_type = 'rsa',
                                       encoding_type = encoding,
                                       is_private_encrypted = (password is not None and len(password) > 0),
                                       private_password = password, public_data = public_encoding,
                                       private_data = private_encoding):
        click.echo('rsa generated failed')
        return


def combine_if_not_empty(hash_mode: str, mode: str) -> str:
    if len(hash_mode) <= 0:
        return mode
    return '{}-{}'.format(mode, hash_mode)


@click.command(name = 'encrypt')
@click.option('-f', '--public-key',
              required = True,
              type = click.STRING,
              help = '公钥文件路径')
@click.option('-i', '--input-data',
              required = True,
              type = click.STRING,
              help = '输入数据，可以直接为字符串，也可以为 base64编码的数据，base64编码的数据需要带上标识 -c')
@click.option('-e', '--encoding',
              type = click.Choice(list(common.encoding_maps.keys())),
              default = 'pem',
              show_default = True,
              help = '密钥格式')
@click.option('-c', '--b64-encoded',
              required = False,
              type = click.BOOL,
              is_flag = True,
              help = '输入数据是否被 base64 编码过')
@click.option('-l', '--input-limit',
              required = False,
              type = click.INT,
              default = 1,
              show_default = True,
              help = '输入内容最大长度，单位为 MB，默认为 1MB，非对称不适合直接加密过长的数据')
@click.option('-m', '--mode',
              required = True,
              default = 'oaep',
              show_default = True,
              type = click.Choice(rsa_encryption_mode),
              help = '加密时的填充模式')
@click.option('-h', '--hash-mode',
              required = False,
              default = 'sha256',
              show_default = True,
              type = click.Choice(list(rsa_hash_map.keys())),
              help = '此参数仅在-m为 oaep 时生效')
@command_perf.timing_decorator
def rsa_encrypt(public_key: click.STRING,
                encoding: click.STRING,
                input_data: click.STRING,
                b64_encoded: click.STRING,
                input_limit: click.INT,
                hash_mode: click.STRING,
                mode: click.STRING):
    if b64_encoded:
        try:
            input_raw_bytes = common.decode_b64_data(input_data)
        except BaseException as e:
            click.echo('invalid b64 encoded data:{}, decoded failed:{}'.format(input_data, e))
            return
    else:
        input_raw_bytes = input_data.encode('utf-8')

    if len(input_raw_bytes) > input_limit * 1024 * 1024:
        click.echo(
            'the data exceeds the maximum bytes limit, limited to:{}Bytes, now:{}Bytes'.format(input_limit * 1024 * 1024,
                                                                                               len(input_raw_bytes)))
        return

    pub_key = common.load_public_key(encoding = encoding, file_path = public_key)
    if pub_key is None:
        return
    cipher = None
    if mode == 'oaep':
        rsa_oaep_padding = padding.OAEP(
            mgf = padding.MGF1(algorithm = rsa_hash_map[hash_mode]()),
            algorithm = rsa_hash_map[hash_mode](),
            label = None,
        )
        cipher = pub_key.encrypt(plaintext = input_raw_bytes, padding = rsa_oaep_padding)
    if mode == 'pkcs1v15':
        hash_mode = ''
        cipher = pub_key.encrypt(plaintext = input_raw_bytes, padding = padding.PKCS1v15())
    click.echo('pub key size:{}\npadding mode:{}\ncipher:{}'.format(pub_key.key_size,
                                                                    combine_if_not_empty(hash_mode, mode),
                                                                    base64.b64encode(cipher).decode('utf-8')))
    return


@click.command(name = 'decrypt')
@click.option('-f', '--private-key',
              required = True,
              type = click.STRING,
              help = '私钥文件路径')
@click.option('-i', '--input-data',
              required = True,
              type = click.STRING,
              help = '输入的密文数据， 必须为base64编码的数据')
@click.option('-e', '--encoding',
              type = click.Choice(list(common.encoding_maps.keys())),
              default = 'pem',
              show_default = True,
              help = '密钥格式')
@click.option('-m', '--mode',
              required = True,
              default = 'oaep',
              show_default = True,
              type = click.Choice(rsa_encryption_mode),
              help = '加密时的填充模式')
@click.option('-h', '--hash-mode',
              required = False,
              default = 'sha256',
              show_default = True,
              type = click.Choice(list(rsa_hash_map.keys())),
              help = '此参数仅在-m为 oaep 时生效')
@click.option('-p', '--password',
              required = False,
              type = click.STRING,
              default = '',
              help = '私钥密码，使用私钥时需要输入正确的密码')
@command_perf.timing_decorator
def rsa_decrypt(private_key: click.STRING,
                input_data: click.STRING,
                encoding: click.STRING,
                mode: click.STRING,
                hash_mode: click.STRING,
                password: click.STRING):
    if password is not None and len(password) > 0:
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = None
    plain = None
    try:  # 密文解码
        input_raw_bytes = common.decode_b64_data(input_data)
    except BaseException as e:
        click.echo('invalid b64 encoded data:{}, decoded failed:{}'.format(input_data, e))
        return
    else:
        pri_key = common.load_private_key(encoding = encoding, file_path = private_key, password_bytes = password_bytes)
        if pri_key is None:
            return
        try:  # 使用私钥根据加密模式解密数据
            if mode == 'oaep':
                rsa_oaep_padding = padding.OAEP(
                    mgf = padding.MGF1(algorithm = rsa_hash_map[hash_mode]()),
                    algorithm = rsa_hash_map[hash_mode](),
                    label = None,
                )
                plain = pri_key.decrypt(input_raw_bytes, rsa_oaep_padding)
            if mode == 'pkcs1v15':
                hash_mode = ''
                plain = pri_key.decrypt(input_raw_bytes, padding.PKCS1v15())
        except BaseException as e:
            click.echo(
                'decrypt failed:{}\nprivate key:{}\npassword:{}\nmode:{}'.format(e, private_key, password,
                                                                                 combine_if_not_empty(hash_mode, mode)))
            return
        else:  # 判断解密的明文是否为字符串
            padding_mode = combine_if_not_empty(hash_mode, mode)
            click.echo('private key password:{}\nkey size:{}'.format(password, pri_key.key_size))
            be_str, ret = common.bytes_to_str(plain)
            if not be_str:
                click.echo('padding mode:{}\nb64 encoded plain:{}'.format(
                    padding_mode, ret))
                return
            else:
                click.echo('padding mode:{}\norigin plain:{}'.format(padding_mode, ret))
                return


@click.command(name = 'sign')
@click.option('-f', '--private-key',
              required = True,
              type = click.STRING,
              help = '私钥文件路径')
@click.option('-e', '--encoding',
              type = click.Choice(list(common.encoding_maps.keys())),
              default = 'pem',
              show_default = True,
              help = '密钥格式')
@click.option('-m', '--mode',
              required = True,
              default = 'pss',
              show_default = True,
              type = click.Choice(rsa_sign_mode),
              help = '签名时的填充模式')
@click.option('-h', '--hash-mode',
              required = False,
              default = 'sha256',
              show_default = True,
              type = click.Choice(list(rsa_hash_map.keys())),
              help = '签名时的哈希算法')
@click.option('-p', '--password',
              required = False,
              type = click.STRING,
              default = '',
              help = '私钥密码，使用私钥时需要输入正确的密码')
@click.option('-i', '--input-data',
              required = True,
              type = click.STRING,
              help = '需要被签名的数据')
@click.option('-c', '--b64-encoded',
              required = False,
              type = click.BOOL,
              is_flag = True,
              help = '输入数据是否被 base64 编码过')
@command_perf.timing_decorator
def rsa_sign(private_key: click.STRING,
             input_data: click.STRING,
             mode: click.STRING,
             hash_mode: click.STRING,
             password: click.STRING,
             encoding: click.STRING,
             b64_encoded: click.BOOL):
    password_bytes = None
    if password is not None and len(password) > 0:
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = None

    if b64_encoded:
        try:
            input_raw_bytes = common.decode_b64_data(input_data)
        except BaseException as e:
            click.echo('invalid b64 encoded data:{}, decoded failed:{}'.format(input_data, e))
            return
    else:
        input_raw_bytes = input_data.encode('utf-8')

    pri_key = common.load_private_key(encoding = encoding, file_path = private_key, password_bytes = password_bytes)
    if pri_key is None:
        return
    # 使用私钥根据签名填充模式进行签名
    try:
        signature = b''
        if mode == 'pss':
            rsa_pss_padding = padding.PSS(
                mgf = padding.MGF1(algorithm = rsa_hash_map[hash_mode]()),
                salt_length = padding.PSS.MAX_LENGTH
            )
            signature = pri_key.sign(
                input_raw_bytes,
                rsa_pss_padding,
                rsa_hash_map[hash_mode](),
            )
        if mode == 'pkcs1v15':
            signature = pri_key.sign(
                input_raw_bytes,
                padding.PKCS1v15(),
                rsa_hash_map[hash_mode](),
            )
    except BaseException as e:
        click.echo('sign failed:{}\nprivate key:{}\npassword:{}\nmode:{}'.format(
            e, private_key, password,
            combine_if_not_empty(hash_mode, mode)))
    else:
        click.echo('key size:{}\nsignature:{}\n{}\nbase64 encoded:{}\nmode:{}'.format(
            pri_key.key_size, signature.hex(), '-' * 16,
            base64.b64encode(signature).decode('utf-8'),
            combine_if_not_empty(hash_mode, mode)))


@click.command(name = 'verify')
@click.option('-f', '--public-key',
              required = True,
              type = click.STRING,
              help = '公钥文件路径')
@click.option('-e', '--encoding',
              type = click.Choice(list(common.encoding_maps.keys())),
              default = 'pem',
              show_default = True,
              help = '密钥格式')
@click.option('-m', '--mode',
              required = True,
              default = 'pss',
              show_default = True,
              type = click.Choice(rsa_sign_mode),
              help = '签名时的填充模式')
@click.option('-h', '--hash-mode',
              required = False,
              default = 'sha256',
              show_default = True,
              type = click.Choice(list(rsa_hash_map.keys())),
              help = '签名时的哈希算法')
@click.option('-i', '--input-data',
              required = True,
              type = click.STRING,
              help = '需要被签名的数据')
@click.option('-c', '--b64-encoded',
              required = False,
              type = click.BOOL,
              is_flag = True,
              help = '输入数据是否被 base64 编码过')
@click.option('-s', '--signature',
              required = False,
              type = click.STRING,
              help = 'base64 编码过的签名值')
@command_perf.timing_decorator
def rsa_verify(public_key: click.STRING,
               input_data: click.STRING,
               b64_encoded: click.BOOL,
               signature: click.STRING,
               mode: click.STRING,
               hash_mode: click.STRING,
               encoding: click.STRING):
    if b64_encoded:
        try:
            input_raw_bytes = common.decode_b64_data(input_data)
        except BaseException as e:
            click.echo('invalid b64 encoded data:{}, decoded failed:{}'.format(input_data, e))
            return
    else:
        input_raw_bytes = input_data.encode('utf-8')

    try:
        signature_raw_bytes = common.decode_b64_data(signature)
    except BaseException as e:
        click.echo('invalid b64 encoded signature, decoded failed:{}'.format(e))
        return

    pub_key = common.load_public_key(encoding = encoding, file_path = public_key)
    if pub_key is None:
        return
    # 使用公钥根据签名验证
    try:
        if mode == 'pss':
            rsa_pss_padding = padding.PSS(
                mgf = padding.MGF1(algorithm = rsa_hash_map[hash_mode]()),
                salt_length = padding.PSS.MAX_LENGTH
            )
            pub_key.verify(
                signature_raw_bytes,
                input_raw_bytes,
                rsa_pss_padding,
                rsa_hash_map[hash_mode](),
            )
        if mode == 'pkcs1v15':
            pub_key.verify(
                signature_raw_bytes,
                input_raw_bytes,
                padding.PKCS1v15(),
                rsa_hash_map[hash_mode](),
            )
    except InvalidSignature as e:
        click.echo('{}\nInvalidSignature!\nkey size:{}\nmode:{}'.format(
            '-' * 16, pub_key.key_size,
            combine_if_not_empty(hash_mode, mode)))
    else:
        click.echo('verify success\nkey size:{}\nmode:{}'.format(
            pub_key.key_size,
            combine_if_not_empty(hash_mode, mode)))


if __name__ == '__main__':
    rsa_group.add_command(generate_key_pair)
    rsa_group.add_command(rsa_encrypt)
    rsa_group.add_command(rsa_decrypt)
    rsa_group.add_command(rsa_sign)
    rsa_group.add_command(rsa_verify)
    rsa_group()
