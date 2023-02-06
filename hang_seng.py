# venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 1/2/2023 6:55 pm
# @Author  : Perye (Pengyu LI)
# @File    : hang_seng.py
# @Software: PyCharm

import os

# ========== Use Flask with Nacos ==========
from flask_with_nacos.app import FlaskWithNacos
from flask import make_response

import app_config


app = FlaskWithNacos(__name__, eval(f'app_config.{os.getenv("FLASK_ENV")}["SERVER_ADDRESSES"]'), 'public')


@app.after_request
def after(resp):
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, PUT, DELETE, CONNECT, OPTIONS, TRACE, PATCH'
    resp.headers['Access-Control-Max-Age'] = '100'
    resp.headers['Access-Control-Allow-Headers'] = '*, Authorization, token, accept, user-agent, content-type, ' \
                                                   'Access-Control-Expose-Headers '
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Expose-Headers'] = 'token, Authorization, accept, user-agent, content-type'
    return resp

# ========== Use Original Flask ==========
# from flask import Flask
# import os
# app = Flask(__name__)
# app.config.from_mapping(eval(f'app_config.{os.getenv("FLASK_ENV")}'))


