import pandas as pd
import db

df = pd.read_csv('./data/NIFTY50Stocks.csv')
df = df.drop(columns = [ 'exchange_token', 'tick_size',
       'lot_size', 'instrument_type', 'segment', 'exchange'])
df = df.rename(columns={"instrument_token": "zerodha_token"})
print(df.columns)
conn = db.connect()
db.execute_mogrify(conn,df,'stock')