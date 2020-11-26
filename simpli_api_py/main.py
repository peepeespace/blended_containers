# uvicorn main:app --reload

import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
import asyncio
import aioredis
import zstandard as zstd
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

redis = None
dctx = zstd.ZstdDecompressor()

app_token = 'blendedrequesttoken'


class DataShape(str, Enum):
    json = 'json'
    array = 'array'


class KeyValueType(str, Enum):
    key = 'key'
    value = 'value'


@app.on_event('startup')
async def startup():
    global redis
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    redis = await aioredis.create_redis_pool(f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/0')


@app.get('/request-token/')
async def request_token():
    return {
        'token': app_token
    }


@app.get('/tickers/')
async def get_tickers(token: str, name: bool = False):
    if token == app_token:
        key = 'SIMPLI_US_TICKERS_LIST' if not name else 'SIMPLI_US_TICKERSNAME_LIST'
        raw = await redis.get(key)
        ticker_list = json.loads(dctx.decompress(raw))
        return {
            'status': '200_SUCCESS',
            'method': 'get_tickers',
            'data': ticker_list,
            'count': len(ticker_list)
        }
    else:
        return JSONResponse(status_code=400, content={'status': '400_ERROR', 'method': 'get_tickers', 'data': None, 'message': 'wrong token'})


@app.get('/types/')
async def get_types(token: str):
    if token == app_token:
        raw = await redis.get('SIMPLI_US_TICKERS_TYPES_LIST')
        typeslist = json.loads(dctx.decompress(raw))
        return {
            'status': '200_SUCCESS',
            'method': 'get_types',
            'data': typeslist,
            'count': len(typeslist)
        }
    else:
        return JSONResponse(status_code=400, content={'status': '400_ERROR', 'method': 'get_tickers', 'data': None, 'message': 'wrong token'})


@app.get('/info/')
async def get_info(token: str, ticker: str = '', stock_type: str = '', ticker_only: bool = False):
    if token == app_token:
        raw = await redis.get('SIMPLI_US_TICKERS_DICT')
        ticker_dict = json.loads(dctx.decompress(raw))

        if ticker != '':
            ticker_dict = ticker_dict.get(ticker)

        if stock_type != '':
            ticker_dict = {key: val for key,
                           val in ticker_dict.items() if val['Type'] == stock_type}

        if ticker_only == True:
            ticker_dict = list(ticker_dict.keys())

        return {
            'status': '200_SUCCESS',
            'method': 'get_info',
            'ticker': ticker,
            'stock_type': stock_type,
            'ticker_only': ticker_only,
            'data': ticker_dict,
            'count': len(ticker_dict.keys()) if type(ticker_dict) == dict else len(ticker_dict)
        }
    else:
        return JSONResponse(status_code=400, content={'status': '400_ERROR', 'method': 'get_tickers', 'data': None, 'message': 'wrong token'})


@app.get('/price/{ticker}/')
async def get_price(ticker: str, token: str, date_from: Optional[str] = '', date_to: Optional[str] = '', format: Optional[DataShape] = 'json', fields: Optional[str] = 'all'):
    # token filter
    if token == app_token:
        tickers = await redis.get('SIMPLI_US_TICKERS_LIST')
        tickerlist = json.loads(dctx.decompress(tickers))
        if ticker not in tickerlist:
            return JSONResponse(status_code=400, content={'status': '400_ERROR', 'method': 'get_price', 'data': None, 'message': 'no such ticker'})
        raw = await redis.get(f'SIMPLI_US_{ticker}_PRICE_LIST')
        pricelist = json.loads(dctx.decompress(raw))

        # date filters
        if (date_from != '') and (date_to == ''):
            pricelist = [d for d in pricelist if d['date'] >= date_from]
        elif (date_to != '') and (date_from == ''):
            pricelist = [d for d in pricelist if d['date'] <= date_to]
        elif (date_to != '') and (date_from != ''):
            pricelist = [d for d in pricelist if (
                d['date'] >= date_from) and (d['date'] <= date_to)]

        # format filters
        if format == 'array':
            if fields == 'all':
                pricelist = [[*d.values()] for d in pricelist]
            else:
                # field filters
                try:
                    fields_list = fields.split(',')
                    pricelist = [list(map(d.get, fields_list))
                                 for d in pricelist]
                except:
                    return JSONResponse(status_code=400, content={'status': '400_ERROR', 'method': 'get_tickers', 'data': None, 'message': 'fields should be in format: x,x,x'})
        elif format == 'json':
            if fields != 'all':
                try:
                    fields_list = fields.split(',')
                    pricelist = [
                        {key: d.get(key)for key in fields_list} for d in pricelist]
                except:
                    return JSONResponse(status_code=400, content={'status': '400_ERROR', 'method': 'get_tickers', 'data': None, 'message': 'fields should be in format: x,x,x'})

        return {
            'status': '200_SUCCESS',
            'method': 'get_price',
            'ticker': ticker,
            'date_from': date_from,
            'date_to': date_to,
            'format': format,
            'fields': fields,
            'data': pricelist,
            'count': len(pricelist)
        }
    else:
        return JSONResponse(status_code=400, content={'status': '400_ERROR', 'method': 'get_tickers', 'data': None, 'message': 'wrong token'})


@app.get('/fundamental/{ticker}/')
async def get_fundamental(ticker: str, token: str, field: Optional[str] = 'all', subfield: Optional[str] = 'all', keyvalue: Optional[KeyValueType] = KeyValueType.value):
    if token == app_token:
        tickers = await redis.get('SIMPLI_US_TICKERS_LIST')
        tickerlist = json.loads(dctx.decompress(tickers))
        if ticker not in tickerlist:
            return JSONResponse(status_code=400, content={'status': '400_ERROR', 'method': 'get_price', 'data': None, 'message': 'no such ticker'})
        raw = await redis.get(f'SIMPLI_US_{ticker}_FUNDAMENTAL_JSON')
        fundamental_json = json.loads(dctx.decompress(raw))
        try:
            fundamental_data = fundamental_json if field == 'all' else fundamental_json[field]
        except:
            fundamental_data = fundamental_json

        try:
            if subfield != 'all':
                fields = subfield.split('.')
                data = fundamental_data
                for f in fields:
                    data = data.get(f)
                fundamental_data = data
        except:
            fundamental_data = None

        if keyvalue == KeyValueType.key:
            try:
                fundamental_data = list(fundamental_data.keys())
            except:
                fundamental_data = fundamental_data

        return {
            'status': '200_SUCCESS',
            'method': 'get_fundamental',
            'field': field,
            'subfield': subfield,
            'keyvalue': keyvalue,
            'data': fundamental_data
        }
    else:
        return JSONResponse(status_code=400, content={'status': '400_ERROR', 'method': 'get_tickers', 'data': None, 'message': 'wrong token'})
