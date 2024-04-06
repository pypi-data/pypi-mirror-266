#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Time: 2024-04-03 23:05:39
import base64

import click
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from easy_encryption_tool import command_perf
from easy_encryption_tool import common

ecc_map = {
    ec.SECP256R1().name: ec.SECP256R1,
    ec.SECP384R1().name: ec.SECP384R1,
    ec.SECP521R1().name: ec.SECP521R1,
    ec.SECP256K1().name: ec.SECP256K1,
}

ecc_hash_map = {
    hashes.SHA256().name: hashes.SHA256,
    hashes.SHA384().name: hashes.SHA384,
    hashes.SHA512().name: hashes.SHA512,
    hashes.SHA3_224().name: hashes.SHA3_224,
    hashes.SHA3_256().name: hashes.SHA3_256,
    hashes.SHA3_384().name: hashes.SHA3_384,
    hashes.SHA3_512().name: hashes.SHA3_512,
}


@click.group(name = 'ecc', short_help = 'ecc签名验签和密钥交换验证工具')
def ecc_group():
    pass


@click.command(name = 'generate')
@click.option('-c', '--curve',
              required = False,
              type = click.Choice(list(ecc_map.keys())),
              default = ec.SECP256K1().name,
              show_default = True,
              help = 'ecc 椭圆曲线类型')
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
def generate(curve: click.STRING,
             encoding: click.STRING,
             file_name: click.STRING,
             password: click.STRING,
             random_password: click.BOOL):
    password, enc = common.private_key_password(random_password, password)
    ecc_private_key = ec.generate_private_key(ecc_map[curve](), default_backend())
    ecc_public_key = ecc_private_key.public_key()
    private_key_encoding = ecc_private_key.private_bytes(
        encoding = common.encoding_maps[encoding],
        format = serialization.PrivateFormat.PKCS8,
        encryption_algorithm = enc
    )
    public_key_encoding = ecc_public_key.public_bytes(
        encoding = common.encoding_maps[encoding],
        format = serialization.PublicFormat.SubjectPublicKeyInfo
    )
    if not common.write_asymmetric_key(file_name_prefix = file_name,
                                       asymmetric_type = 'ecc',
                                       encoding_type = encoding,
                                       is_private_encrypted = (password is not None and len(password) > 0),
                                       private_password = password,
                                       public_data = public_key_encoding,
                                       private_data = private_key_encoding):
        click.echo('ecc generated failed')
    return


@click.command(name = 'ecdh')
@click.option('-a', '--alice-pub-key',
              required = True,
              type = click.STRING,
              help = '你自己的公钥文件的路径如: ./alice_public.pem')
@click.option('-k', '--alice-pri-key',
              required = True,
              type = click.STRING,
              help = '你自己的私钥文件的路径如: ./alice_private.pem')
@click.option('-p', '--password',
              required = False,
              type = click.STRING,
              default = '',
              help = '你自己的私钥的密码，如果创建时设置了密码，那么在使用私钥时需要输入正确的密码')
@click.option('-b', '--bob-pub-key',
              required = True,
              type = click.STRING,
              help = '对方的公钥文件的路径如: ./bob_public.pem')
@click.option('-e', '--encoding',
              type = click.Choice(list(common.encoding_maps.keys())),
              default = 'pem',
              show_default = True,
              help = '密钥格式')
@click.option('-l', '--length',
              required = False,
              type = click.IntRange(16, 64),
              default = 32,
              show_default = True,
              help = '派生密钥的长度，默认 32 字节，长度范围[16 -- 64]')
@click.option('-s', '--salt',
              required = True,
              type = click.STRING,
              default = 'hello,world1234567890!@#$%^&*()_+{}:";<>?/',
              show_default = True,
              help = '用于增加派生密钥安全性的盐值，两边必须提供一样的盐值')
@click.option('-c', '--context',
              required = True,
              type = click.STRING,
              default = 'ecc handshake context data',
              show_default = True,
              help = '用于增加派生密钥安全性的上下文信息，两边必须提供一样的上下文数据')
@command_perf.timing_decorator
def key_exchange(alice_pub_key: click.STRING,
                 alice_pri_key: click.STRING,
                 bob_pub_key: click.STRING,
                 encoding: click.STRING,
                 password: click.STRING,
                 length: click.INT,
                 salt: click.STRING,
                 context: click.STRING):
    if password is not None and len(password) > 0:
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = None
    alice_pub = common.load_public_key(encoding = encoding, file_path = alice_pub_key)
    if alice_pub is None:
        return
    alice_pri = common.load_private_key(encoding = encoding, file_path = alice_pri_key, password_bytes = password_bytes)
    if alice_pri is None:
        return
    bob_pub = common.load_public_key(encoding = encoding, file_path = bob_pub_key)
    if bob_pub is None:
        return
    salt_bytes = None
    if salt is not None and len(salt) > 0:
        salt_bytes = salt.encode('utf-8')
    context_bytes = None
    if context is not None and len(context) > 0:
        context_bytes = context.encode('utf-8')
    shared_secret_alice = alice_pri.exchange(ec.ECDH(), bob_pub)
    derived_key = HKDF(
        algorithm = hashes.SHA3_512(),  # 默认使用安全级别最高的哈希函数
        length = length,
        salt = salt_bytes,
        info = context_bytes,
        backend = default_backend()
    ).derive(shared_secret_alice)
    click.echo('curve name:{}\nderived key:{}\nlength:{}'.format(
        alice_pri.curve.name,
        base64.b64encode(derived_key).decode('utf-8'),
        len(derived_key)
    ))


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
@click.option('-h', '--hash-mode',
              required = False,
              default = 'sha256',
              show_default = True,
              type = click.Choice(list(ecc_hash_map.keys())),
              help = '签名时的哈希算法')
@click.option('-p', '--password',
              required = False,
              type = click.STRING,
              default = '',
              help = '私钥密码，如果生成时设置了密码那么在使用私钥时需要输入正确的密码')
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
def ecc_sign(private_key: click.STRING,
             input_data: click.STRING,
             hash_mode: click.STRING,
             password: click.STRING,
             encoding: click.STRING,
             b64_encoded: click.BOOL):
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

    try:

        signature = pri_key.sign(input_raw_bytes, ec.ECDSA(ecc_hash_map[hash_mode]()))
        click.echo('curve name:{}\nkey size:{}\nsignature:{}\nbase64 encoded:{}\nmode:{}'.format(
            pri_key.curve.name, pri_key.key_size, signature.hex(),
            base64.b64encode(signature).decode('utf-8'), ec.ECDSA.__name__))
    except BaseException as e:
        click.echo('sign failed:{}\nprivate key:{}\npassword:{}\nmode:{}'.format(e, private_key, password,
                                                                                 ec.ECDSA.__name__))


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
@click.option('-h', '--hash-mode',
              required = False,
              default = 'sha256',
              show_default = True,
              type = click.Choice(list(ecc_hash_map.keys())),
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
def ecc_verify(public_key: click.STRING,
               input_data: click.STRING,
               b64_encoded: click.BOOL,
               signature: click.STRING,
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
        pub_key.verify(signature_raw_bytes, input_raw_bytes, ec.ECDSA(ecc_hash_map[hash_mode]()))
    except InvalidSignature as e:
        click.echo('InvalidSignature!\nkey size:{}\nmode:{}'.format(
            pub_key.key_size, ec.ECDSA.__name__))
    else:
        click.echo('curve name:{}\nverify success\nkey size:{}\nmode:{}'.format(
            pub_key.curve.name, pub_key.key_size, ec.ECDSA.__name__))


if __name__ == '__main__':
    ecc_group.add_command(generate)
    ecc_group.add_command(key_exchange)
    ecc_group.add_command(ecc_sign)
    ecc_group.add_command(ecc_verify)
    ecc_group()
