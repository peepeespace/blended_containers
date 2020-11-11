import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blended.settings")
application = get_wsgi_application()

from data.models import ETF, Buysell, Factor, General, Index, MarketCap, Price

import redis
import psycopg2
import pandas as pd
import numpy as np
import json
import datetime

def clean(txt):
    return txt.strip().replace(',', '')


def remove_data(data):
    remove_bool = any(map(str.isdigit, data)) and ('풋' in data or '콜' in data)
    remove_bool = remove_bool or ('ETN' in data)
    return remove_bool


def make_django_price_data(date, data):
    return [
        Price(
            date=date,
            code=dt[0],
            name=dt[1],
            strt_prc=int(dt[2]) if dt[2] != '' else None,
            high_prc=int(dt[3]) if dt[3] != '' else None,
            low_prc=int(dt[4]) if dt[4] != '' else None,
            cls_prc=int(dt[5]) if dt[5] != '' else None,
            adj_prc=int(dt[6]) if dt[6] != '' else None,
            trd_qty=float(dt[7]) if dt[7] != '' else None,
            trd_amt=float(dt[8]) if dt[8] != '' else None,
            shtsale_trd_qty=float(dt[9]) if dt[9] != '' else None
        ) for dt in data
        if not remove_data(dt[1])
    ]

def make_django_mkt_cap_data(date, data):
    return [
        MarketCap(
            date=date,
            code=dt[0],
            name=dt[1],
            comm_stk_qty=int(dt[2]) if dt[2] != '' else None,
            pref_stk_qty=int(dt[3]) if dt[3] != '' else None
        ) for dt in data
        if not remove_data(dt[1])
    ]

def make_django_factor_data(date, data):
    return [
        Factor(
            date=date,
            code=dt[0],
            name=dt[1],
            per=float(dt[2]) if dt[2] != '' else None,
            pbr=float(dt[3]) if dt[3] != '' else None,
            pcr=float(dt[4]) if dt[4] != '' else None,
            psr=float(dt[5]) if dt[5] != '' else None,
            divid_yield=float(dt[6]) if dt[6] != '' else None
        ) for dt in data
        if not remove_data(dt[1])
    ]

def make_django_buysell_data(date, data):
    return [
        Buysell(
            date=date,
            code=dt[0],
            name=dt[1],
            forgn_b=int(dt[2]) if dt[2] != '' else None,
            forgn_s=int(dt[3]) if dt[3] != '' else None,
            forgn_n=int(dt[4]) if dt[4] != '' else None,
            private_b=int(dt[5]) if dt[5] != '' else None,
            private_s=int(dt[6]) if dt[6] != '' else None,
            private_n=int(dt[7]) if dt[7] != '' else None,
            inst_sum_b=int(dt[8]) if dt[8] != '' else None,
            inst_sum_s=int(dt[9]) if dt[9] != '' else None,
            inst_sum_n=int(dt[10]) if dt[10] != '' else None,
            trust_b=int(dt[11]) if dt[11] != '' else None,
            trust_s=int(dt[12]) if dt[12] != '' else None,
            trust_n=int(dt[13]) if dt[13] != '' else None,
            pension_b=int(dt[14]) if dt[14] != '' else None,
            pension_s=int(dt[15]) if dt[15] != '' else None,
            pension_n=int(dt[16]) if dt[16] != '' else None,
            etc_inst_b=int(dt[17]) if dt[17] != '' else None,
            etc_inst_s=int(dt[18]) if dt[18] != '' else None,
            etc_inst_n=int(dt[19]) if dt[19] != '' else None
        ) for dt in data
        if not remove_data(dt[1])
    ]

def make_django_etf_data(date, data):
    return [
        ETF(
            date=date,
            code=dt[0],
            name=dt[1],
            cls_prc=float(dt[2]) if dt[2] != '' else None,
            trd_qty=int(dt[3]) if dt[3] != '' else None,
            trd_amt=int(dt[4]) if dt[4] != '' else None,
            etf_nav=float(dt[5]) if dt[5] != '' else None,
            spread=float(dt[6]) if dt[6] != '' else None
        ) for dt in data
        if not remove_data(dt[1])
    ]

def make_django_index_data(date, data):
    return [
        Index(
            date=date,
            code=dt[0],
            name=dt[1],
            strt_prc=float(dt[2]) if dt[2] != '' else None,
            high_prc=float(dt[3]) if dt[3] != '' else None,
            low_prc=float(dt[4]) if dt[4] != '' else None,
            cls_prc=float(dt[5]) if dt[5] != '' else None,
            trd_qty=float(dt[6]) if dt[6] != '' else None,
            trd_amt=float(dt[7]) if dt[7] != '' else None
        ) for dt in data
        if not remove_data(dt[1])
    ]


def send_info():
    ls = './raw_data'
    file = [f for f in os.listdir(ls) if 'stockinfo.csv' in f][0]
    date = file.split('.')[0]
    if General.objects.filter(date=date).exists() == False:
        with open('{}/{}'.format(ls, file), 'r') as csv:
            d = csv.read()
        d_l = d.split(date)
        d_l = [data.split('|') for data in d_l[1:]]
        d_l = [
            [clean(dt) for dt in data[1:]]
            for data in d_l
        ]
        d_s = [
            General(
                date=date,
                code=dt[0],
                name=dt[1],
                stk_kind=dt[2],
                mkt_gb=dt[3],
                mkt_cap=int(dt[4]),
                mkt_cap_size=dt[5],
                frg_hlg=float(dt[6]),
                mgt_gb=dt[7]
            ) for dt in d_l
            if not remove_data(dt[1])
        ]
        General.objects.bulk_create(d_s, batch_size=1000)


def send_data(data_type):
    ls = f'./raw_data/{data_type}'
    files = [f for f in os.listdir(ls) if '.csv' in f]
    cnt = 0

    def data_exists(data_type, date):
        if data_type == 'ohlcv':
            exists = Price.objects.filter(date=date).exists()
        elif data_type == 'mkt_cap':
            exists = MarketCap.objects.filter(date=date).exists()
        elif data_type == 'factor':
            exists = Factor.objects.filter(date=date).exists()
        elif data_type == 'buysell':
            exists = Buysell.objects.filter(date=date).exists()
        elif data_type == 'etf':
            exists = ETF.objects.filter(date=date).exists()
        elif data_type == 'index':
            exists = Index.objects.filter(date=date).exists()
        return exists

    try:
        saved_list = open(f'{data_type}_saved.txt', 'r').read().split('\n')
    except:
        saved_list = []

    print('saved_list: ', saved_list)
    for f in files:
        date = f.split('.')[0]
        if date not in saved_list:
            if data_exists(data_type, date) == False:
                with open('{}/{}'.format(ls, f), 'r') as csv:
                    d = csv.read()
                d_l = d.split(date)
                d_l = [data.split('|') for data in d_l[1:]]
                d_l = [
                    [clean(dt) for dt in data[1:]]
                    for data in d_l
                ]

                if data_type == 'ohlcv':
                    d_s = make_django_price_data(date, d_l)
                elif data_type == 'mkt_cap':
                    d_s = make_django_mkt_cap_data(date, d_l)
                elif data_type == 'factor':
                    d_s = make_django_factor_data(date, d_l)
                elif data_type == 'buysell':
                    d_s = make_django_buysell_data(date, d_l)
                elif data_type == 'etf':
                    d_s = make_django_etf_data(date, d_l)
                elif data_type == 'index':
                    d_s = make_django_index_data(date, d_l)

                try:
                    if data_type == 'ohlcv':
                        Price.objects.bulk_create(d_s, batch_size=1000)
                    elif data_type == 'mkt_cap':
                        MarketCap.objects.bulk_create(d_s, batch_size=1000)
                    elif data_type == 'factor':
                        Factor.objects.bulk_create(d_s, batch_size=1000)
                    elif data_type == 'buysell':
                        Buysell.objects.bulk_create(d_s, batch_size=1000)
                    elif data_type == 'etf':
                        ETF.objects.bulk_create(d_s, batch_size=1000)
                    elif data_type == 'index':
                        Index.objects.bulk_create(d_s, batch_size=1000)

                    cnt = cnt + 1
                    print(f'({cnt} / {len(files)}) {date} {data_type} saved to DB')
                    with open(f'{data_type}_saved.txt', 'a') as saved_t:
                        saved_t.write(f'{date}\n')
                except Exception as e:
                    print(e)
                    print(f'{date} {data_type} errored')
                    with open(f'{data_type}_err.txt', 'a') as err_t:
                        err_t.write(f'{date}\n')


if __name__ == '__main__':
    data_types = ['ohlcv', 'mkt_cap', 'factor', 'buysell', 'etf', 'index']

    send_info()

    for t in data_types:
        send_data(t)