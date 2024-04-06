#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Time: 2024-04-05 15:16:05
import binascii
import hashlib
import os

import click
from cryptography.hazmat.primitives import hashes, serialization
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
extensions = 'extension_keys'

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


def get_cert_info(cert: X509):
    cert_info_map = {
        version:
            '{}-{}'.format(cert.to_cryptography().version.name, cert.to_cryptography().version.value),
        serial_number:
            cert.get_serial_number(),
        signature_hash_algorithm: cert.to_cryptography().signature_hash_algorithm.name,
        tbs_certificate_bytes: binascii.hexlify(cert.to_cryptography().tbs_certificate_bytes).decode('utf-8').upper(),
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

    if cert.get_extension_count() > 0:
        cert_info_map[extensions] = []
    for i in range(0, cert.get_extension_count()):
        cert_info_map[extensions].append(cert.get_extension(i).get_short_name().decode('utf-8'))
    return cert_info_map


# # todo: 待调试对证书的验签操作
# def verify_cert_signature(cert: X509):
#     try:
#         pub_key = cert.to_cryptography().public_key()
#         cert_signature = cert.to_cryptography().signature
#         hash_alg = cert.to_cryptography().signature_hash_algorithm
#         cert_tbs_certificate_bytes = cert.to_cryptography().tbs_certificate_bytes
#         signature_algorithm_oid = cert.to_cryptography().signature_algorithm_oid
#         if cert.get_pubkey().type() == crypto.TYPE_RSA:
#             rsa_padding = None
#             if signature_algorithm_oid in (x509.OID_RSA_WITH_SHA1,
#                                            x509.OID_RSA_WITH_SHA224,
#                                            x509.OID_RSA_WITH_SHA256,
#                                            x509.OID_RSA_WITH_SHA384,
#                                            x509.OID_RSA_WITH_SHA512):
#                 rsa_padding = padding.PKCS1v15()
#                 print('pkcs1v15 padding')
#             elif signature_algorithm_oid in (x509.OID_RSASSA_PSS,):
#                 rsa_padding = padding.PSS(
#                     mgf = padding.MGF1(algorithm = hash_alg),
#                     salt_length = padding.PSS.MAX_LENGTH,
#                 )
#                 print('pss padding')
#             pub_key.verify(signature = cert_signature,
#                            data = cert_tbs_certificate_bytes,
#                            algorithm = hash_alg,
#                            padding = rsa_padding)
#         elif cert.get_pubkey().type() == crypto.TYPE_EC:
#             pub_key.verify(cert_signature, cert_tbs_certificate_bytes, ec.ECDSA(hash_alg))
#     except InvalidSignature as e:
#         print("The certificate signature is not valid.")
#         raise e


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
        input_file = common.read_from_file(cert_file)
        file_size = os.stat(cert_file).st_size
        if file_size > 1024 * 10:  # 限制证书文件不能超过 10KB
            click.echo('cert file:{} size:{}Bytes, too large cert file'.format(cert_file, file_size))
            return
    except BaseException as e:
        click.echo('read from:{} failed:{}'.format(cert_file, e))
        return
    else:
        try:
            cert_raw_bytes = input_file.read_n_bytes(file_size)
            if encoding == 'pem':
                cert_type = crypto.FILETYPE_PEM
            else:
                cert_type = crypto.FILETYPE_ASN1
            cert = crypto.load_certificate(cert_type, cert_raw_bytes)
        except BaseException as e:
            click.echo('error loading certificate:{}, error:{}'.format(cert_file, e))
        else:
            try:
                data = get_cert_info(cert)
            except BaseException as e:
                click.echo('parse cert file error:{}'.format(e))
            else:
                click.echo('------- basic info: -------')
                for i in cert_info_keys:
                    if i in data.keys():
                        click.echo('{}: {}'.format(i, data[i]))
                # try:
                #     verify_cert_signature(cert)
                # except BaseException as e:
                #     click.echo('verify certificate signature failed:{}'.format(e))
                # else:
                if verbose:
                    click.echo('------- verbose info: -------')
                    for i in verbose_info_keys:
                        if i in data.keys():
                            click.echo('{}: {}'.format(i, data[i]))


if __name__ == '__main__':
    parse_x509_cert_file()
