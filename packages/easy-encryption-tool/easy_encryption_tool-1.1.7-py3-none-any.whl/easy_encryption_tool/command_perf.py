#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Time: 2024-04-04 11:19:31
import hashlib
import time
from datetime import datetime

import click


def timing_decorator(func):
    def wrapper(*args, **kwargs):
        now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")[:-3]
        unique_flag = hashlib.sha3_512(now.encode('utf-8')).hexdigest()[-16:]
        click.echo(f"\n------ {unique_flag} begin@{now} ------")
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        click.echo(f"------ {unique_flag} took {(end_time - start_time) * 1000:.3f} milli-seconds to execute ------\n")
        return result

    return wrapper
