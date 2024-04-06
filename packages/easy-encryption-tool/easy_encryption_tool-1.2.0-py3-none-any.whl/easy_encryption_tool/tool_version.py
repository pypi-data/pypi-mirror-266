#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Time: 2024-03-30 22:02:07

import platform
import sys
from typing import Dict

import click

from easy_encryption_tool import command_perf


def sys_info() -> Dict[str, str]:
    return {
        'PythonVersion': sys.version,
        'ApiVersion': sys.api_version,
        'OSPlatform': sys.platform,
        'OSProcessor': platform.platform(),
        'BytesEndian': sys.byteorder,
    }


tool_version_info = 'v1.0.0'
info = sys_info()


@click.command(name = 'version', short_help = '展示当前版本信息以及运行时信息')
@command_perf.timing_decorator
def show_version():
    click.echo('tool-version:{}\npython:{}\nos:{}\nchip:{}\nbyte-order:{}'.format(
        tool_version_info,
        info['PythonVersion'],
        info['OSPlatform'],
        info['OSProcessor'],
        info['BytesEndian'],
    ))
