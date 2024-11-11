#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib


def get_str_md5(content):

    m = hashlib.md5(str(content).encode())
    return m.hexdigest()
