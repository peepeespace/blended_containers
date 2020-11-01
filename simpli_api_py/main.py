# uvicorn main:app --reload

import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from enum import Enum
from typing import Optional
from pydantic import BaseModel
import asyncio
import aioredis
import zstandard as zstd
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
redis = None
dctx = zstd.ZstdDecompressor()


class ModelName(str, Enum):
    alexnet = 'alexnet'
    resnet = 'resnet'
    lenet = 'lenet'


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


class ResponseItem(BaseModel):
    name: str


@app.on_event('startup')
async def startup():
    global redis
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    redis = await aioredis.create_redis_pool(f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/0')


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/test/{test_id}')
async def test_item(test_id: int):
    return {'test_id': test_id}


@app.get('/model/{model_name}')
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {'model_name': model_name, 'message': 'hello'}

    if model_name.value == 'lenet':
        return {'model_name': model_name, 'message': 'hello'}

    return {'model_name': model_name, 'message': 'hello'}


@app.get('/items/')
async def read_items(skip: int = 0, limit: int = 10, q: Optional[str] = None):
    return {'skip': skip, 'limit': limit, 'q': q}


@app.get('/tickers/')
async def get_tickers():
    raw = await redis.get('SIMPLI_US_TICKERS_LIST')
    tickerlist = json.loads(dctx.decompress(raw))
    return tickerlist


@app.post(
    '/items/',
    response_model=ResponseItem,
    summary='returns back item',
    description='this is a post endpoint for items'
)
async def create_items(item: Item):
    if item.name != 'name':
        return JSONResponse(status_code=404, content={
                            'status': 'ERROR', 'type': 'NO_NAME', 'message': 'there is no such name'})
    return item
