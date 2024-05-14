#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib


def get_str_md5(content):
    """
    计算字符串md5
    :param content:
    :return:
    """
    # 创建md5对象
    m = hashlib.md5(str(content).encode())
    return m.hexdigest()
