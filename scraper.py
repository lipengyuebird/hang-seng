# venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2/2/2023 10:03 pm
# @Author  : Perye (Pengyu LI)
# @File    : scraper.py
# @Software: PyCharm

from typing import Dict
import requests
import json
from dateutil import parser

import util.currencies
from extensions import cache


@cache.memoize(timeout=3600)
def scrape_exchange_rate_hkd() -> Dict:
    tt_data = json.loads(requests.get(
        'https://rbwm-api.hsbc.com.hk/pws-hk-hase-rates-papi-prod-proxy/v1/fxtt-exchange-rates'
    ).text)

    last_updated = parser.parse(tt_data['lastUpdateTime']).isoformat()
    tt_data = tt_data['fxttExchangeRates']

    note_data = json.loads(requests.get(
        'https://rbwm-api.hsbc.com.hk/pws-hk-hase-rates-papi-prod-proxy/v1/fxnotes-exchange-rates'
    ).text)['fxnoteExchangeRates']

    note_result = {item['ccyDisplayCode']: {
        'banknotes_bank_buy': float(item['noteBuyRate']) if item['noteBuyRate'] else None,
        'banknotes_bank_sell': float(item['noteSellRate']) if item['noteSellRate'] else None,
    } for item in note_data}

    return {item['ccyDisplayCode']: {
        'telegraphic_transfer_bank_buy': float(item['ttBuyRate']) if item['ttBuyRate'] else None,
        'telegraphic_transfer_bank_sell': float(item['ttSellRate'])if item['ttSellRate'] else None,
        'last_updated': last_updated,
        **(note_result.get(item['ccyDisplayCode']) or {'banknotes_bank_buy': None, 'banknotes_bank_sell': None})
    } for item in tt_data}


def clear_cache(base_currency: str, currency: str):
    assert base_currency.upper() in util.currencies.allowed_currencies
    assert currency.upper() in util.currencies.allowed_currencies
    cache.delete_memoized(eval('scrape_exchange_rate_' + base_currency.lower()))
