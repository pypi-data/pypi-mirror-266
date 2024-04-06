#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Time: 2024-04-05 15:16:05
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict

import click
import requests
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.x509 import Extensions
from OpenSSL import crypto
from OpenSSL.crypto import X509

from easy_encryption_tool import command_perf, common

version = 'version'
serial_number = 'serial_number'
signature_algorithm = 'signature_algorithm'
signature_hash_algorithm = 'signature_hash_algorithm'
tbs_certificate_bytes = 'tbs_certificate_bytes'
issuer = 'issuer'
valid_before = 'valid_before'
valid_after = 'valid_after'
subject = 'subject'
public_key_bits = 'public_key_bits'
public_key_modules = 'public_key_modules'
public_key_exponent = 'public_key_exponent'
public_key_type = 'public_key_type'
public_key_fingerprints = 'public_key_fingerprints'
signature = 'signature'
certificate_fingerprints = 'certificate_fingerprints'
extension_count = 'extension_count'
extensions = 'extensions_detail'

ca_issuer = None
ocsp = None

AuthorityInformationAccessCAIssuers = 'caIssuers'
AuthorityInformationAccessOCSP = 'OCSP'
AuthorityInformationAccess = ('x509.AuthorityInformationAccess', x509.AuthorityInformationAccess)
BasicConstraints = ('x509.BasicConstraints', x509.BasicConstraints)
KeyUsage = ('x509.KeyUsage', x509.KeyUsage)
SubjectKeyIdentifier = ('x509.SubjectKeyIdentifier', x509.SubjectKeyIdentifier)
SubjectAlternativeName = ('x509.SubjectAlternativeName', x509.SubjectAlternativeName)
CRLDistributionPoints = ('x509.CRLDistributionPoints', x509.CRLDistributionPoints)
ExtendedKeyUsage = ('x509.ExtendedKeyUsage', x509.ExtendedKeyUsage)
FreshestCR = ('x509.FreshestCRL', x509.FreshestCRL)
NameConstraints = ('x509.NameConstraints', x509.NameConstraints)
PolicyConstraints = ('x509.PolicyConstraints', x509.PolicyConstraints)

cert_extensions = [
    AuthorityInformationAccess,
    BasicConstraints,
    KeyUsage,
    SubjectKeyIdentifier,
    SubjectAlternativeName,
    CRLDistributionPoints,
    ExtendedKeyUsage,
    FreshestCR,
    NameConstraints,
    PolicyConstraints,
]

verbose_info_keys = [
    tbs_certificate_bytes,
    public_key_exponent,
    public_key_modules,
    public_key_fingerprints,
    signature,
    certificate_fingerprints,
    extension_count,
    extensions
]

cert_info_keys = [
    version, serial_number, signature_algorithm,
    signature_hash_algorithm,
    issuer, valid_before, valid_after, subject,
    public_key_bits, public_key_type,
]


def parse_cert_extensions(cert_extensions_raw: Extensions) -> Dict[str, Any]:
    ret = {}
    for i in cert_extensions:
        try:
            ext_value = cert_extensions_raw.get_extension_for_class(i[1])
        except x509.ExtensionNotFound:
            ret[i[0]] = {
                'ERROR': 'x509.ExtensionNotFound',
                'oid': '',
                'value': {},
                'critical': False,
            }
            continue
        else:
            ret[i[0]] = {
                'oid': ext_value.oid.dotted_string,
                'critical': ext_value.critical,
                'value': ext_value.value.__repr__(),
            }
            if i[0] == AuthorityInformationAccess[0]:
                ret[i[0]]['value'] = {
                    AuthorityInformationAccessCAIssuers: '',
                    AuthorityInformationAccessOCSP: '',
                }
                for v in ext_value.value:
                    if v.access_method._name == AuthorityInformationAccessCAIssuers:
                        ret[i[0]]['value'][AuthorityInformationAccessCAIssuers] = v.access_location.value

                    if v.access_method._name == AuthorityInformationAccessOCSP:
                        ret[i[0]]['value'][AuthorityInformationAccessOCSP] = v.access_location.value

    return ret


def get_cert_info(cert: X509):
    cert_info_map = {
        version:
            '{}-{}'.format(cert.to_cryptography().version.name, cert.to_cryptography().version.value),
        serial_number:
            cert.get_serial_number(),
        signature_hash_algorithm: cert.to_cryptography().signature_hash_algorithm.name,
        issuer:
            '{}|{}|{}'.format(cert.get_issuer().organizationName, cert.get_issuer().commonName,
                              cert.get_issuer().countryName), valid_before: cert.get_notBefore().decode('utf-8'),
        valid_after: cert.get_notAfter().decode('utf-8'),
        subject:
            '{}|{}|{}'.format(cert.get_subject().organizationName, cert.get_subject().countryName,
                              cert.get_subject().commonName), public_key_bits: cert.get_pubkey().bits(),
        public_key_type:
            '{}({}:RSA|{}:DSA|{}:EC|{}:DH)'.format(cert.get_pubkey().type(),
                                                   crypto.TYPE_RSA,
                                                   crypto.TYPE_DSA,
                                                   crypto.TYPE_EC,
                                                   crypto.TYPE_DH, ),
        public_key_fingerprints:
            hashlib.sha256(
                cert.get_pubkey().to_cryptography_key().public_bytes(
                    encoding = serialization.Encoding.DER,
                    format = serialization.PublicFormat.SubjectPublicKeyInfo)).hexdigest().upper(),
        signature:
            hex(int.from_bytes(cert.to_cryptography().signature, byteorder = 'big')).upper(),
        certificate_fingerprints:
            cert.digest(hashes.SHA256.name).decode('utf-8').upper(),
        extension_count:
            str(cert.get_extension_count())
    }

    if cert.get_pubkey().type() == crypto.TYPE_RSA:
        cert_info_map[signature_algorithm] = 'PKCS #1 RSA Encryption'
        cert_info_map[public_key_modules] = format(cert.get_pubkey().to_cryptography_key().public_numbers().n, 'x').upper(),
        cert_info_map[public_key_exponent] = format(cert.get_pubkey().to_cryptography_key().public_numbers().e, 'x').upper(),
    elif cert.get_pubkey().type() == crypto.TYPE_EC:
        cert_info_map[signature_algorithm] = 'Elliptic Curve Public Key'
    cert_info_map[extensions] = parse_cert_extensions(cert.to_cryptography().extensions)
    return cert_info_map


def load_cert_data(cert_file: str) -> bytes:
    """
        加载证书原始数据
    """
    try:
        input_file = common.read_from_file(cert_file)
        file_size = os.stat(cert_file).st_size
        if file_size > 1024 * 10:  # 限制证书文件不能超过 10KB
            click.echo('cert file:{} size:{}Bytes, too large cert file'.format(cert_file, file_size))
            return b''
    except BaseException as e:
        click.echo('read from:{} failed:{}'.format(cert_file, e))
        raise (e)
    else:
        try:
            cert_raw_bytes = input_file.read_n_bytes(file_size)
        except BaseException as e:
            raise e
        else:
            return cert_raw_bytes


def read_file_from_url(url: str) -> bytes | None:
    if url is None or len(url) <= 0:
        return None
    # print(url)
    # 发送GET请求到URL
    response = requests.get(url)
    # 确保请求成功
    if response.status_code == 200:
        # 读取文件内容
        file_content = response.content
        return file_content
    else:
        return None


def verify_cert_signature(cert: X509,
                          ca_cert: X509):
    try:
        cert_signature = cert.to_cryptography().signature
        hash_alg = cert.to_cryptography().signature_hash_algorithm
        cert_tbs_certificate_bytes = cert.to_cryptography().tbs_certificate_bytes
        signature_algorithm_oid = cert.to_cryptography().signature_algorithm_oid
        ca_pub_key = ca_cert.to_cryptography().public_key()
        if ca_cert.get_pubkey().type() == crypto.TYPE_RSA:
            rsa_padding = None
            if signature_algorithm_oid in (x509.OID_RSA_WITH_SHA1,
                                           x509.OID_RSA_WITH_SHA224,
                                           x509.OID_RSA_WITH_SHA256,
                                           x509.OID_RSA_WITH_SHA384,
                                           x509.OID_RSA_WITH_SHA512):
                rsa_padding = padding.PKCS1v15()
                # print('pkcs1v15 padding')
            elif signature_algorithm_oid in (x509.OID_RSASSA_PSS,):
                rsa_padding = padding.PSS(
                    mgf = padding.MGF1(algorithm = hash_alg),
                    salt_length = padding.PSS.MAX_LENGTH,
                )
                # print('pss padding')
            ca_pub_key.verify(signature = cert_signature,
                              data = cert_tbs_certificate_bytes,
                              algorithm = hash_alg,
                              padding = rsa_padding)
        if ca_cert.get_pubkey().type() == crypto.TYPE_EC:
            ca_pub_key.verify(cert_signature, cert_tbs_certificate_bytes, ec.ECDSA(hash_alg))
    except InvalidSignature as e:
        raise InvalidSignature('signature verified failed')


def verify_cert_file_signature_from_ca_issuer(cert: X509, ca_issuer_url: str):
    try:
        ca_issuer_cert_raw = read_file_from_url(ca_issuer_url)
    except BaseException as e:
        raise e
    else:
        for i in [crypto.FILETYPE_PEM, crypto.FILETYPE_ASN1]:
            try:
                ca_cert = crypto.load_certificate(i, ca_issuer_cert_raw)
            except BaseException as e:
                if i == crypto.FILETYPE_ASN1:  # 如果所有类型全部遍历完成但是还是报错的话
                    raise ValueError('ca issuer cert load failed, tried format:{}, issuer:{}'.format(
                        common.encoding_maps.keys(),
                        ca_issuer_url))
                if i == crypto.FILETYPE_PEM:
                    continue
            else:
                try:
                    verify_cert_signature(cert, ca_cert)
                except BaseException as e:
                    raise InvalidSignature('verify cert signature failed, ca issuer:{}'.format(ca_issuer_url))
                else:
                    return


@click.command(name = 'cert-parse', short_help = '解析 pem 或 der 格式的证书')
@click.option('-f', '--cert-file',
              required = True,
              type = click.STRING,
              help = '证书文件路径')
@click.option('-e', '--encoding',
              required = True,
              type = click.Choice(list(common.encoding_maps.keys())),
              default = 'pem',
              show_default = True,
              help = '密钥格式')
@click.option('-v', '--verbose',
              required = False,
              type = click.BOOL,
              is_flag = True,
              default = False,
              show_default = True,
              help = '是否展示详细信息')
@command_perf.timing_decorator
def parse_x509_cert_file(cert_file: click.STRING, encoding: click.STRING, verbose: click.BOOL):
    try:
        # 读取原始数据
        cert_raw_bytes = load_cert_data(cert_file)
    except BaseException as e:
        return
    else:
        try:
            if encoding == 'pem':
                cert_type = crypto.FILETYPE_PEM
            else:
                cert_type = crypto.FILETYPE_ASN1
            # 按照 pem 或者 der 格式读取数据
            cert = crypto.load_certificate(cert_type, cert_raw_bytes)
        except BaseException as e:
            click.echo('loading cert file:{} as format:{} failed:{}'.format(cert_file, encoding, e))
            return
        else:
            try:
                # 解析证书数据内容，尤其获取 AIA（Authority Information Access） 信息
                # 由这个信息读取根证书，进而获取根证书的公钥信息
                data = get_cert_info(cert)
            except BaseException as e:
                click.echo('parse cert file info error:{}'.format(e))
            else:
                exts = data[extensions]
                if AuthorityInformationAccess[0] in exts.keys():
                    click.echo('------- verify signature: -------')
                    try:
                        ca_issuer_url = exts[AuthorityInformationAccess[0]]['value'][AuthorityInformationAccessCAIssuers]
                        # ocsp_url = exts[AuthorityInformationAccess[0]]['value'][AuthorityInformationAccessOCSP]
                        try:
                            verify_cert_file_signature_from_ca_issuer(cert, ca_issuer_url)
                        except BaseException as e:
                            click.echo('verify cert signature failed:{}, ca issuer:{}'.format(e, ca_issuer_url))
                        else:
                            click.echo('verify cert signature success\nca issuer:{}\n'.format(ca_issuer_url))
                    except BaseException:
                        click.echo('NO CA ISSUER FOUND\n')

                click.echo('------- basic info: -------')
                for i in cert_info_keys:
                    if i in data.keys():
                        ret = data[i]
                        if isinstance(data[i], dict):
                            ret = json.dumps(data[i], indent = '    ')
                        click.echo('{}: {}'.format(i, ret))

                if verbose:
                    click.echo('\n------- verbose info: -------')
                    for i in verbose_info_keys:
                        if i in data.keys():
                            ret = data[i]
                            if isinstance(data[i], dict):
                                ret = json.dumps(data[i], indent = '    ')
                            click.echo('{}: {}'.format(i, ret))


if __name__ == '__main__':
    parse_x509_cert_file()
