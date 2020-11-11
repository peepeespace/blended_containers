import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blended.settings")
application = get_wsgi_application()

from data.models import USPrice


import json
import redis
from dotenv import load_dotenv
import zstandard as zstd

dctx = zstd.ZstdDecompressor()

load_dotenv()

USDATA_REDIS_HOST = os.getenv('USDATA_REDIS_HOST')
USDATA_REDIS_PASSWORD = os.getenv('USDATA_REDIS_PASSWORD')
KRDATA_REDIS_HOST = os.getenv('KRDATA_REDIS_HOST')
KRDATA_REDIS_PASSWORD = os.getenv('KRDATA_REDIS_PASSWORD')

us_cache = redis.StrictRedis(host=USDATA_REDIS_HOST, port=6379, password=USDATA_REDIS_PASSWORD)
kr_cache = redis.StrictRedis(host=KRDATA_REDIS_HOST, port=6379, password=KRDATA_REDIS_PASSWORD)


def save_us_price_to_db():
    # saving US data to DB
    price_keys = us_cache.keys('SIMPLI_US_*_PRICE_LIST')

    cnt = 0

    for key in price_keys:
        code = str(key).split('_')[2]
        price_raw = us_cache.get(key)
        price_data = json.loads(dctx.decompress(price_raw))
        price_data_list = [
            USPrice(
                date=dt['date'],
                code=code,
                open_price=dt['open'],
                high_price=dt['high'],
                low_price=dt['low'],
                close_price=dt['close'],
                adjusted_close=dt['adjusted_close'],
                volume=dt['volume']
            ) for dt in price_data
        ]
        # USPrice.objects.filter(code=code).delete()
        USPrice.objects.bulk_create(price_data_list, batch_size=1000)
        
        cnt = cnt + 1
        print(f'({cnt} / {len(price_keys)}) {code} saved to DB')


# ohlcv = us_cache.get('SIMPLI_US_ABPYX_PRICE_LIST')

# # ohlcv = kr_cache.get('BLENDED_20120112_OHLCV')
# data = json.loads(dctx.decompress(ohlcv))
# print(data[0])
# # print(data['771289'])


if __name__ == '__main__':
    save_us_price_to_db()