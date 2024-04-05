#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Time: 2024-04-01 09:04:43
import random
import string
import sys

import click

from easy_encryption_tool import command_perf, common

special_characters = '&=!@#$%^*()_+`'
characters: str = string.ascii_lowercase + \
                  string.ascii_uppercase + \
                  string.digits + \
                  special_characters


def generate_random_str(length: int) -> str:
    part_1 = ''.join(random.choices(string.ascii_lowercase, k = length // 5))
    part_2 = ''.join(random.choices(special_characters, k = length // 5))
    part_3 = ''.join(random.choices(string.ascii_uppercase, k = length // 5))
    part_4 = ''.join(random.choices(string.digits, k = length // 5))
    part_5 = ''.join(random.choices(characters, k = length - (len(part_1) + len(part_2) + len(part_3) + len(part_4))))
    all_chars_list = list(part_1 + part_2 + part_3 + part_4 + part_5)
    random.shuffle(all_chars_list)
    return ''.join(all_chars_list)


@click.command(name = 'random-str', short_help = '随机字符串生成器')
@click.option('-l', '--length',
              required = False,
              type = click.IntRange(min = 1, max = sys.maxsize),
              default = 32,
              show_default = True,
              help = '最小生成一个字节字符串，最大长度由系统最大整型值决定')
@click.option('-o', '--output-file',
              required = False,
              type = click.STRING,
              default = '',
              help = '指定输出的文件，文件需要具有可写权限')
@command_perf.timing_decorator
def get_random_str(length: int, output_file: click.STRING):
    write_to_output = None
    if output_file is not None and len(output_file) > 0:
        try:
            write_to_output = common.write_to_file(output_file)
        except BaseException as e:
            click.echo('try write to {} failed'.format(output_file))
            return

    # 每次只生成 32 字节，避免字符串过长导致内存占用太多
    default_block = 32
    for i in range(0, length // default_block + 1):
        if length <= 0:
            break
        if length <= default_block:
            default_block = length
        tmp = generate_random_str(default_block)
        if write_to_output is not None:
            if not write_to_output.write_bytes(tmp.encode('utf-8')):
                return
        else:
            click.echo(tmp, nl = False)
        length -= default_block
    if write_to_output is not None:
        click.echo('write to {} success'.format(output_file))
    else:
        click.echo(nl = True)


if __name__ == '__main__':
    get_random_str()
