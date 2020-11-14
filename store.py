import pandas as pd

from kiteconnect import KiteConnect
import nsepy 

 
import db
from config import config

import logging

# Import date and timdelta class 
# from datetime module 
from datetime import date 
from datetime import timedelta 
from datetime import datetime

def getHistoryData(kite,ins_token,date1,date2,interval):
    result = kite.historical_data(ins_token,date1,date2, interval)
    return result

def getStockData():
    conn = db.connect()
    nifty50Map = db.query(conn,'SELECT id,zerodha_token, symbol, name FROM stock')
    nifty50Map = nifty50Map.set_index('symbol').to_dict()
    nifty50Map = nifty50Map['id']
    return nifty50Map

def getKiteConnector(reqToken):
    zerodhaParams = config(filename ='zerodha.ini',section='zerodha')
    kite = KiteConnect(zerodhaParams['api_key'])
    data = kite.generate_session(reqToken,zerodhaParams['api_secret'] )
    kite.set_access_token(data["access_token"])
    return kite
def getFullPriceData(kite,dayRange,interval):
    stockData = getStockData()
    today = date.today()
    date1 = (today - timedelta(days = dayRange)).strftime("%Y-%m-%d") +' 00:00:00'
    date2 = today.strftime("%Y-%m-%d") +' 23:59:59'
    fullDf = pd.DataFrame()
    for instr in stockData:
        rawData = getHistoryData(kite,instr,date1,date2,interval)
        df = pd.DataFrame(rawData)        
        df['stock_id'] = pd.Series([stockData[instr] for x in range(len(df.index))], index=df.index)
        if(fullDf.empty):
            fullDf = df
        else:
            fullDf = fullDf.append(df)
    return fullDf
def writeToDB(df):
    conn = db.connect()    
    df = df.rename(columns={"date": "timestamp"})
    print(df)
    db.execute_mogrify(conn,df,'stock_price')


def getNSEPyHistoryData(stock,start,end):
    rawData = nsepy.get_history(symbol=stock, start=start, end=end)
    rawData = pd.DataFrame(rawData)
    rawData.reset_index(inplace=True)
    rawData = rawData.rename(columns={
        'Open':'open',
        'High':'high',
        'Low':'low',
        'Close':'close',
        'Volume' :'volume',
        'Date':'date'
    })
    return rawData

def getNSEPyFullPriceData(dayRange):
    stockData = getStockData()
    today = date.today()
    date1 = (today - timedelta(days = dayRange))
    date2 = today
    fullDf = pd.DataFrame()
    for instr in stockData:
        print(instr,stockData[instr])        
        df = getNSEPyHistoryData(instr,date1,date2)     
        df['stock_id'] = pd.Series([stockData[instr] for x in range(len(df.index))], index=df.index)
        if(fullDf.empty):
            fullDf = df
        else:
            fullDf = fullDf.append(df)
    fullDf = (fullDf[['date','open','high','low','close','volume','stock_id']])  
    return fullDf