# venv/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2/2/2023 4:23 pm
# @Author  : Perye (Pengyu LI)
# @File    : currencies.py
# @Software: PyCharm

allowed_currencies = [
    'HKD',
    'USD',
    'CNY',
    'ISK',
    'JPY',
    'KRW',
    'MXN',
    'MYR',
    'NOK',
    'NZD',
    'PHP',
    'PLN',
    'RON',
    'RUB',
    'SEK',
    'SGD',
    'THB',
    'TRY',
    'ZAR'
]


def validate_currency(currency: str):
    return isinstance(currency, str) and currency.upper() in allowed_currencies
