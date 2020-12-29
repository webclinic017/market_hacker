from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime as datetime  # For datetime objects
import pandas as pd  # To manage paths
import sys  # To find out the script name (in argv[0])
import ta


# Import the backtrader platform
import backtrader as bt
import model
from indicators.VolumeWeightedAveragePrice import VolumeWeightedAveragePrice as vwap

# Create a Stratey
class VWAPMACDCO(bt.Strategy):
    sold = False
    sold_price = None
    stoploss = 1
    target = 2
    params = (
        # Standard MACD Parameters
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9)
    )
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        #print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.vwap = vwap(period = 10 )
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)
        
        self.mcross = bt.indicators.CrossOver( self.macd.signal,self.macd.macd)
        self.mcross.plotinfo.plot = False
    
    def next(self):       
        if self.sold == False:
            if self.data.close[0] > self.data.open[0]:
                if (self.vwap[0] < self.data.close[0]
                    and self.mcross[0] > 0.0):
                    self.sold = True
                    self.sell()
                    self.sold_price = self.data.close[0]
                    self.log('sold @ Close, %.2f' % self.data.close[0])
                    return
        if self.sold == True:
            diff = -(self.data.close[0] - self.sold_price)
            diffpercent = (diff*100/self.sold_price)

            #buytrigger = ((self.vwap[0]) > self.data.close[0])
            buytrigger = False
            if diff > 0 and diffpercent < self.target:
                buytrigger = True
                self.log(''' target reached ''')
            if diff < 0 and diffpercent > self.stoploss:
                self.log(f''' stoploss triggered {diffpercent} ''')
                buytrigger = True
                
            if buytrigger == True:
                self.buy()
                self.sold = False
                self.log('sold @ Close, %.2f' % self.data.close[0])

if __name__ == '__main__':

    # Get data from database
    allMinutePriceData = model.getMinutePriceData(start = datetime(2020,11,15) ,end = datetime(2020,12,4))       
    finalOutput = {}
    symbols = allMinutePriceData['symbol'].unique().tolist()
    for symbol in symbols:
        #print(symbol)        
        minutePriceData = allMinutePriceData[allMinutePriceData['symbol'] == symbol]
        minutePriceData = minutePriceData.set_index('datetime')    
        output = {}
        df = minutePriceData.resample('10T', origin='start', closed='left', label='left').agg({'open': 'first',
                                                                        'high': 'max',
                                                                        'low': 'min',
                                                                        'close': 'last',
                                                                        'volume':'sum'}).dropna()  
        print('stopping resampling..')    
        minutePriceData = bt.feeds.PandasData(
            dataname=df)
        cerebro = bt.Cerebro()
        # Add a strategy
        cerebro.addstrategy(VWAPMACDCO)
        # Add the Data Feeds to Cerebro
        cerebro.adddata(minutePriceData)
        # Set our desired cash start
        cerebro.broker.setcash(10000.0)

        cerebro.addsizer(bt.sizers.AllInSizerInt)
        # Print out the starting conditions
        startvalue =  cerebro.broker.getvalue()
        print('Starting Portfolio Value: %.2f' % startvalue)

        # Run over everything
        cerebro.run()
        #cerebro.plot(style='candle',volume = False)

        endvalue =  cerebro.broker.getvalue()
        # Print out the final result
        print('Final Portfolio Value: %.2f' % endvalue)
        output[df.index.date[0]] = ((endvalue-startvalue)*100/startvalue) 
        #break

        output = pd.Series(output)
        finalOutput[symbol] = output
    result = pd.DataFrame(finalOutput)

    print(result)
    print(result.sum())
    print(result.sum().mean())
    print(result.sum(axis =1))    
    print('Daily avg')
    print(result.sum(axis =1).mean())
    
    