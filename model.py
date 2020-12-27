import db
def getPriceData(dayInterval):
    conn = db.connect()
    df = db.query(conn,
    f'''SELECT s.symbol,s.name,sp.* from stock_price sp 
        INNER JOIN stock s ON s.id = sp.stock_id
        WHERE timestamp > now() -  INTERVAL '{dayInterval} days'
        ORDER BY s.name,timestamp
        ''')
    df = df.rename(columns={'timestamp':'datetime'})
    return df

def getMinutePriceData(start,end,stockSymbol = ''):
    nameClause = ''
    if stockSymbol != '':
        nameClause = f''' and s.symbol = '{stockSymbol}' '''
    conn = db.connect()
    sqlQuery = f'''SELECT s.symbol,s.name,sp.* from stock_price_intraday sp 
        INNER JOIN stock s ON s.id = sp.stock_id {nameClause}
        WHERE timestamp >= '{start}' and timestamp <= '{end}' 
        ORDER BY s.name,timestamp
        '''
    df = db.query(conn,sqlQuery)
    df = df.rename(columns={'timestamp':'datetime'})
    return df

def getStockData():
    conn = db.connect()
    nifty50Map = db.query(conn,'SELECT id,zerodha_token, symbol, name FROM stock')
    nifty50Map = nifty50Map.set_index('symbol').to_dict()
    nifty50Map = nifty50Map['id']
    return nifty50Map