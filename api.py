# venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2/2/2023 10:55 pm
# @Author  : Perye (Pengyu LI)
# @File    : api.py
# @Software: PyCharm
import json

from flask import request
from flask_parameter_validation import ValidateParameters, Route, Json, Query

from hang_seng import app, bus
from error_handler import handle_param_validation
import util.currencies
import scraper


@app.route('/rate')
@ValidateParameters(handle_param_validation)
def get_rate(
        base_currency: str = Query('HKD', func=util.currencies.validate_currency),
        currency: str = Query('HKD', func=util.currencies.validate_currency)
):
    if 'GET' == request.method:
        scraper_func = getattr(scraper, 'scrape_exchange_rate_' + base_currency.lower())
        return scraper_func().get(currency) or {}
    elif 'DELETE' == request.method:
        scraper.clear_cache(base_currency, currency)


@bus.handle('hang-seng')
def update(msg):
    msg = msg.value.decode('ascii')
    try:
        d = json.loads(msg)
        scraper.clear_cache(d['base_currency'], d['currency'])
    except:
        print(msg)
