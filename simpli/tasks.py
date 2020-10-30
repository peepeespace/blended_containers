import os
import json
import requests
import redis
import zstandard as zstd
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
RABBIT_HOST = os.getenv('RABBIT_HOST')
RABBIT_USER = os.getenv('RABBIT_USER')
RABBIT_PASSWORD = os.getenv('RABBIT_PASSWORD')
RESPONSIBILITY = os.getenv('RESPONSIBILITY') # 데이터를 나누어 맡을 부분
API_KEY = os.getenv(f'API_{RESPONSIBILITY}')

app = Celery(
    'simpli',
    broker=f'amqp://{RABBIT_USER}:{RABBIT_PASSWORD}@{RABBIT_HOST}:5672//',
    backend=f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/0'
)
app.conf.celery_timezone = 'Asia/Seoul'
app.conf.celery_enable_utc = True
app.conf.beat_schedule = {
    'save tickers (every 3 hours)': {
        'task': 'simpli.save_tickers',
        'schedule': crontab(minute=0, hour='*/3'),
        'args': (),
    },
}

cctx = zstd.ZstdCompressor()
dctx = zstd.ZstdDecompressor()

keyname = {
    'complete tickers': 'SIMPLI_COMPLETE_TICKERS',
    'us tickers': 'SIMPLI_US_TICKERS',
    'us tickers list': 'SIMPLI_US_TICKERS_LIST'
}

def cache_conn():
    redis_client = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASSWORD)
    return redis_client

def set_list(redis_client, data):
    response = redis_client.rpush(data[0], *data[1:])
    return response # returns 1 or 0

def get_list(redis_client, key, type='str'):
    response = redis_client.lrange(key, 0, -1)
    temp = response
    if type == 'int':
        try:
            is_int = int(response[0])
            response = list(map(lambda x: int(x), response))
        except ValueError:
            response = temp
    elif type == 'str':
        response = list(map(lambda x: x.decode('utf-8'), response))
    return response

def add_to_list(redis_client, key, data):
    response = redis_client.rpush(key, data)
    return response # returns 1 or 0

def save(redis_client, key, data):
    redis_client.set(
        key,
        cctx.compress(json.dumps(data).encode('utf8'))
    )

def get(redis_client, key):
    return json.loads(dctx.decompress(redis_client.get(key)))


redis_client = cache_conn()


###########################################################
###########################################################
@app.task(name='simpli.save_tickers', soft_time_limit=1000)
def save_tickers():
    url = f'https://eodhistoricaldata.com/api/exchange-symbol-list/US?fmt=json&api_token={API_KEY}'
    res = requests.get(url)
    data = res.json()
    
    # save complete data first
    save(redis_client, keyname['complete tickers'], data)   

    us_data = [d for d in data if d['Country'] == 'USA']
    save(redis_client, keyname['us tickers'], us_data)

    us_data_tickerlist = [d['Code'] for d in us_data]
    save(redis_client, keyname['us tickers list'], us_data_tickerlist)


# if __name__ == "__main__":
#     save_tickers()