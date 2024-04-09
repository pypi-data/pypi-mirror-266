#  dates.py
#  Project: sensorialytics
#  Copyright (c) 2021 Sensoria Health Inc.
#  All rights reserved

import datetime

import pandas

__all__ = ['get_age', 'get_date', 'get_date_ymd', 'get_date_y_m_d',
           'get_date_ymdhm']


def get_age(birth_date: (datetime.datetime, str),
            ref_date: (datetime.datetime, str)):
    if isinstance(birth_date, str) or pandas.isna(birth_date):
        birth_date = pandas.to_datetime(birth_date)

    if isinstance(ref_date, str) or pandas.isna(ref_date):
        ref_date = pandas.to_datetime(ref_date)

    corr = (ref_date.month, ref_date.day) < (birth_date.month, birth_date.day)
    age = ref_date.year - birth_date.year - corr

    return age


def get_date(n_days=0):
    now = datetime.datetime.now() + datetime.timedelta(n_days)
    date = {
        'ye': f'{now.year:4}',
        'mo': f'{now.month:2}',
        'da': f'{now.day:2}',
        'ho': f'{now.hour:2}',
        'mi': f'{now.minute:2}'
    }
    return date


def get_date_ymd(n_days=0):
    date = get_date(n_days)
    return date['ye'] + date['mo'] + date['da']


def get_date_y_m_d(n_days=0):
    date = get_date(n_days)
    return date['ye'] + '-' + date['mo'] + '-' + date['da']


def get_date_ymdhm(n_days=0):
    date = get_date(n_days)
    return date['ye'] + date['mo'] + date['da'] + '-' + date['ho'] + date['mi']
