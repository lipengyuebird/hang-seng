# venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2/2/2023 4:16 pm
# @Author  : Perye (Pengyu LI)
# @File    : error_handler.py
# @Software: PyCharm

def handle_param_validation(err):
    return {
        'code': '400',
        'message': 'Bad Request'
    }, 400

