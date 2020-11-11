import os
import time
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

ohlcv_sql = """
SELECT date, code, adj_prc FROM data_price;
"""

def get_db():
    return psycopg2.connect(
        database=os.getenv('DBNAME'),
        user=os.getenv('DBUSER'),
        password=os.getenv('DBPW'),
        host=os.getenv('DBHOST'),
        port=os.getenv('DBPORT')
    )

start = time.time()
db = get_db()
df = pd.read_sql(ohlcv_sql, db)
pivot_df = pd.pivot_table(
    df,
    values='adj_prc',
    index='date',
    columns='code',
    dropna=False
)
end = time.time()

print('retrieving data took: ' + str(end - start))

print(pivot_df)