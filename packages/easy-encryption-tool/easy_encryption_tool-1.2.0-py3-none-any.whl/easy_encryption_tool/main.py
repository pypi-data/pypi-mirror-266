#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Time: 2024-03-30 15:41:41

import click

from easy_encryption_tool import aes_command, cert_parse, ecc_command, hmac_command, random_str, rsa_command, tool_version

"""
name (str): 命令组的名称。如果未提供，将使用装饰的函数的名称。

commands (dict): 一个字典，其中键是命令名称，值是命令函数。这允许你在装饰器内部直接定义命令，而不是通过单独的 @click.command() 装饰器。

invoke_without_command (bool): 如果为 True，则在没有提供子命令的情况下调用组时，将调用组函数本身。
这允许组函数作为默认命令或作为一组共享选项的容器。

chain (bool): 如果为 True，则允许在单个调用中组合多个命令。每个命令的输出将作为下一个命令的输入。

context_settings (dict): 一个字典，用于修改传递给命令回调的 Context 对象的默认设置。

add_help_option (bool): 如果为 False，则不会为命令组添加 --help 选项。

subcommand_metavar (str): 在帮助输出中，用于描述子命令的元变量。默认是 "COMMAND"。

epilog (str): 在帮助输出的末尾添加的文本。
"""


@click.group(name = 'easy_encryption_tool', short_help = '易加密小工具')
def encryption_tool():
    pass


encryption_tool.add_command(tool_version.show_version)
encryption_tool.add_command(aes_command.aes_command)
encryption_tool.add_command(random_str.get_random_str)

encryption_tool.add_command(hmac_command.hmac_command)

rsa_command.rsa_group.add_command(rsa_command.generate_key_pair)
rsa_command.rsa_group.add_command(rsa_command.rsa_encrypt)
rsa_command.rsa_group.add_command(rsa_command.rsa_decrypt)
rsa_command.rsa_group.add_command(rsa_command.rsa_sign)
rsa_command.rsa_group.add_command(rsa_command.rsa_verify)
encryption_tool.add_command(rsa_command.rsa_group)

ecc_command.ecc_group.add_command(ecc_command.generate)
ecc_command.ecc_group.add_command(ecc_command.key_exchange)
ecc_command.ecc_group.add_command(ecc_command.ecc_sign)
ecc_command.ecc_group.add_command(ecc_command.ecc_verify)
encryption_tool.add_command(ecc_command.ecc_group)

encryption_tool.add_command(cert_parse.parse_x509_cert_file)

if __name__ == '__main__':
    encryption_tool()
