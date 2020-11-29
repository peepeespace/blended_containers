import os
import json
import requests
import redis
import zstandard as zstd
import sentry_sdk
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
RABBIT_HOST = os.getenv('RABBIT_HOST')
RABBIT_USER = os.getenv('RABBIT_USER')
RABBIT_PASSWORD = os.getenv('RABBIT_PASSWORD')
RESPONSIBILITY = os.getenv('RESPONSIBILITY')  # 데이터를 나누어 맡을 부분
API_KEY = os.getenv(f'API_{RESPONSIBILITY}')
WORKER_COUNT = int(os.getenv('WORKER_COUNT'))
print(f'[Started] Worker {RESPONSIBILITY}. API KEY: {API_KEY}')

sentry_sdk.init(
    "https://05806a5a14a14d0cb8bef35b555bef20@o158142.ingest.sentry.io/5444337",
    traces_sample_rate=1.0
)

app = Celery(
    'simpli',
    broker=f'amqp://{RABBIT_USER}:{RABBIT_PASSWORD}@{RABBIT_HOST}:5672//',
    backend=f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/0'
)
app.conf.celery_timezone = 'Asia/Seoul'
app.conf.celery_enable_utc = True
app.conf.beat_schedule = {
    'save tickers, price, fundamental data (every 12 hours)': {
        'task': 'simpli.distribute_tasks',
        'schedule': crontab(minute=0, hour='*/12'),
        'args': (),
    },
}

cctx = zstd.ZstdCompressor()
dctx = zstd.ZstdDecompressor()


def cache_conn():
    redis_client = redis.Redis(
        host=REDIS_HOST, port=6379, password=REDIS_PASSWORD)
    return redis_client


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
@app.task(name='simpli.distribute_tasks')
def distribute_tasks():
    save_tickers()
    for i in range(WORKER_COUNT):
        save_data.delay(i + 1)


@app.task(name='simpli.save_tickers')
def save_tickers():
    tickers = {}

    # US, KO, KQ --> eod, fundamentals, div
    # INDX --> eod, fundamentals
    exchange_list = ['US', 'KO', 'KQ', 'INDX']

    for exchange in exchange_list:
        url = f'https://eodhistoricaldata.com/api/exchange-symbol-list/{exchange}?fmt=json&api_token={API_KEY}'
        res = requests.get(url)
        tickers[exchange] = res.json()

    total_tickerslist = []

    for exchange, exchange_tickers in tickers.items():
        data = exchange_tickers

        # Complete dictionary of security data provided by edohistorical (dict)
        data_dict = {d['Code']: d for d in data}
        save(
            redis_client,
            f'SIMPLI_{exchange}_TICKERS_DICT',
            data_dict
        )

        # Changed Filtered USA securities to list with tickers only (list)
        data_tickerlist = [d['Code'] for _, d in data_dict.items()]
        save(
            redis_client,
            f'SIMPLI_{exchange}_TICKERS_LIST',
            data_tickerlist
        )

        # Changed Filtered USA securities to list with tickers, name only (list)
        data_tickernamelist = [[d['Code'], d['Name']] for _, d in data_dict.items()]
        save(
            redis_client,
            f'SIMPLI_{exchange}_TICKERSNAME_LIST',
            data_tickernamelist
        )

        # US, KO, KQ에서 펀드, 채권 등 불필요한 정보 제외하기
        filter_type = ['Preferred Stock', 'Common Stock', 'Preferred Share', 'ETF', 'INDEX']
        data_filtered_list = []
        for _, val in data_dict.items():
            if val['Type'] in filter_type:

                # 보통주, 우선주, ETF로 한글 명칭으로 바꿔주기
                if val['Type'] == 'Preferred Stock' or val['Type'] == 'Preferred Share':
                    stock_type = '우선주'
                elif val['Type'] == 'Common Stock':
                    stock_type = '보통주'
                elif val['Type'] == 'ETF':
                    stock_type = 'ETF'
                elif val['Type'] == 'INDEX':
                    stock_type = '지수'

                data_filtered_list.append([
                    val['Code'],
                    val['Name'],
                    val['Country'],
                    val['Exchange'],
                    val['Currency'],
                    stock_type
                ])
        total_tickerslist = total_tickerslist + data_filtered_list
        save(
            redis_client,
            f'SIMPLI_{exchange}_FILTERED_TICKERSNAMELIST',
            data_filtered_list
        )

        # Type of all the securities in all US, KO, KQ, INDX exchanges (list)
        sec_types = list(set(d['Type'] for _, d in data_dict.items()))
        save(
            redis_client,
            f'SIMPLI_{exchange}_TICKERS_TYPES_LIST',
            sec_types
        )

    save(
        redis_client,
        'SIMPLI_FILTERED_TICKERSNAMELIST',
        total_tickerslist
    )
    
    # Divide tickers list by worker count (to divide work load among celery workers)
    # 이 정보를 기반으로 워커들이 데이터를 저장한다
    idx_step = len(total_tickerslist) // WORKER_COUNT
    start_idx = 0
    end_idx = idx_step
    data_list_dict = {}

    for i in range(WORKER_COUNT):
        data_list_dict[str(i + 1)] = total_tickerslist[start_idx:end_idx]
        start_idx = end_idx
        if i == WORKER_COUNT - 2:
            end_idx = len(total_tickerslist)
        else:
            end_idx = (i + 2) * idx_step

    for num, val in data_list_dict.items():
        save(
            redis_client,
            f'SIMPLI_WORKER_{num}_TICKERS_LIST',
            val
        )


@app.task(name='simpli.save_data')
def save_data(responsibility_num):
    worker_num = int(responsibility_num)
    api_key = os.getenv(f'API_{worker_num}')

    try:
        if redis_client.exists(f'SIMPLI_WORKER_{worker_num}_DONE'):
            done_cnt = int(redis_client.get(
                f'SIMPLI_WORKER_{worker_num}_DONE'))
        else:
            redis_client.set(f'SIMPLI_WORKER_{worker_num}_DONE', 0)
            done_cnt = 0

        data_tickerlist = get(
            redis_client, f'SIMPLI_WORKER_{worker_num}_TICKERS_LIST')

        cnt = 0

        for i in range(len(data_tickerlist)):
            if cnt < done_cnt:
                cnt = cnt + 1
                print(
                    f'Skipping request: ({cnt} / {len(data_tickerlist)}) until {done_cnt}')
                continue
            else:
                exchange = data_tickerlist[i][3]
                ticker = data_tickerlist[i][0]

                ##### STEP 1 #####
                # Price data request and save
                url = f'https://eodhistoricaldata.com/api/eod/{ticker}.{exchange}?fmt=json&api_token={api_key}'
                res = requests.get(url)
                try:
                    price_data = res.json()
                    save(
                        redis_client,
                        f'SIMPLI_{exchange}_{ticker}_PRICE_LIST',
                        price_data
                    )
                except:
                    # json decode error
                    print(res)
                    print(res.content)
                    print(f'Skipping {ticker}.{exchange} price data. Error')

                ##### STEP 2 #####
                # Fundamental data request and save
                url = f'https://eodhistoricaldata.com/api/fundamentals/{ticker}.{exchange}?fmt=json&api_token={api_key}'
                res = requests.get(url)
                try:
                    fundamental_data = res.json()
                    save(
                        redis_client,
                        f'SIMPLI_{exchange}_{ticker}_FUNDAMENTAL_JSON',
                        fundamental_data
                    )
                except:
                    # json decode error
                    print(res)
                    print(res.content)
                    print(f'Skipping {ticker}.{exchange} fundamental data. Error')

                ##### STEP 3 #####
                # Dividends data request and save
                # INDX는 dividend 정보 받지 않기
                if exchange != 'INDX':
                    url = f'https://eodhistoricaldata.com/api/div/{ticker}.{exchange}?fmt=json&api_token={api_key}'
                    res = requests.get(url)
                    try:
                        dividend_data = res.json()
                        save(
                            redis_client,
                            f'SIMPLI_{exchange}_{ticker}_DIVIDEND_LIST',
                            dividend_data
                        )
                    except:
                        # json decode error
                        print(res)
                        print(res.content)
                        print(f'Skipping {ticker}.{exchange} dividend data. Error')

                cnt = cnt + 1
                done_cnt = done_cnt + 1
                if done_cnt == len(data_tickerlist):
                    redis_client.set(f'SIMPLI_WORKER_{worker_num}_DONE', 0)
                else:
                    redis_client.set(
                        f'SIMPLI_WORKER_{worker_num}_DONE', done_cnt)
                print(f'({done_cnt} / {len(data_tickerlist)}) {ticker} DONE')

    except Exception as e:
        print('Error:')
        print(e)
        sentry_sdk.capture_exception(e)
        save_data(worker_num)


if __name__ == "__main__":
    save_tickers()
    # save_data()
    # get_korean_tickers()

    # print(get(redis_client, 'SIMPLI_COMPLETE_TICKERS_DICT'))
