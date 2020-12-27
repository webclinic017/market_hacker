from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime 
from datetime import time # For datetime objects
import pandas as pd  # To manage paths
import sys  # To find out the script name (in argv[0])
import ta

# Import the backtrader platform
import backtrader as bt
import model
from indicators.supertrend import SuperTrend as SuperTrend
# Create a Stratey
class SuperTrendStat(bt.Strategy):
    opening_low = None
    opening_high = 0
    bought = False
    already_traded = False
    bought_price = None
    stoploss = 20
    target = 30
    sl_hit = 0
    tg_hit = 0
    c = 40

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):  
        if(self.datas[0].datetime.datetime(0).time() <= time(9, 30)):        
            if self.datas[0].datetime.datetime(0).time() == time(9, 15):  
                self.opening_low = self.data.low[0]            
            if (self.opening_high < self.data.high[0]):                        
                    self.opening_high = self.data.high[0]
                    self.opening_range = (self.opening_high - self.opening_low) + self.c
                    self.target = self.opening_range 
                    self.stoploss = (self.opening_range)         
            return

        if (self.bought == False 
                and self.opening_high < self.data.close[0]
                and self.already_traded != True):
            self.bought = True
            self.buy()
            self.bought_price = self.data.close[0]
            self.log(f''' buy triggered on {self.data.close[0]} ''')
            return

        if (self.bought == True and self.already_traded != True ):
            if((self.data.close[0] >= (self.bought_price + self.target))):
                self.first_bool = False
                self.second_bool = False
                self.bought = False
                self.sell()
                self.already_traded = True            
                self.tg_hit += 1
                self.log(' sell Close, %.2f' % self.data.close[0])
                return            
        if (self.bought == True and self.data.close[0] < (self.bought_price - self.stoploss) ):
            self.first_bool = False
            self.bought = False
            self.sell()
            self.already_traded = True            
            self.sl_hit += 1            
            self.log(''' xxxxxxxxxxxx DANGER xxxxx ''')
            self.log(f''' sell  @ stoploss Close {self.data.close[0]},{self.bought_price}:{self.data.close[0] - self.bought_price}''')

if __name__ == '__main__':

    # self.data.close[0] < self.data.open[0] or Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    # Get data from database
       

    output = {}
    allMinutePriceData = model.getMinutePriceData(start = datetime(2020,8,18) ,end = datetime(2020,12,25,0,0),
    stockSymbol = 'BANKNIFTY20DECFUT')    
    DFList = [group[1] for group in allMinutePriceData.groupby(allMinutePriceData['datetime'].dt.date)]        
    for df in DFList:  
        df = df.set_index('datetime')
        print(df.index.date[0])
        cerebro = bt.Cerebro()
        minutePriceData = bt.feeds.PandasData(
            dataname=df)
        # Add a strategy
        cerebro.addstrategy(SuperTrendStat)
        # Add the Data Feeds to Cerebro
        cerebro.adddata(minutePriceData)
        # Set our desired cash start
        cerebro.broker.setcash(745000.0)

        cerebro.addsizer(bt.sizers.AllInSizerInt)
        # Print out the starting conditions
        startvalue =  cerebro.broker.getvalue()
        
        print('Starting Portfolio Value: %.2f' % startvalue)

        # Run over everything
        cerebro.run()

        # cerebro.plot(style='candle',volume = False)

        endvalue =  cerebro.broker.getvalue()
        # Print out the final result
        print('Final Portfolio Value: %.2f' % endvalue)
        output[df.index.date[0]] = ((endvalue-startvalue)*100/startvalue) 

    output = pd.Series(output)
    #output.to_csv('output/supertrend.csv',header = ['P/L %'])    
    #print(output)
    print(output.mean())
    print(output.sum())