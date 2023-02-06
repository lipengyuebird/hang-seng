# venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2/2/2023 10:54 pm
# @Author  : Perye (Pengyu LI)
# @File    : extensions.py
# @Software: PyCharm

from hang_seng import app

from flask_caching import Cache

cache = Cache(app)
