import urllib
from typing import Optional


from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

import store
from pattern_matrix import pattern_matrix

templates = Jinja2Templates(directory="templates")

app = FastAPI()
kite = None
@app.get("/patternMatrix/{dayRange}")
def read_root(dayRange,request: Request):
    global candlestick_patterns
    stocks = pattern_matrix(dayRange)
    return stocks

@app.get("/")
def zerodha(request_token,load_data = False,dayRange = None):
    global kite
    kite = store.getKiteConnector(request_token)
    if  load_data == 'True':
        df = store.getFullPriceData(kite,int(dayRange),'minute')
    return {"sucess": True}

@app.get("/stocks")
def get_stocks():
    res = store.getStockData()
    return res


@app.get("/loadData/{source}/{dayRange}")
def load_data(source,dayRange):
    if source == 'zerodha':
        encodedParams = urllib.parse.quote(f"""load_data=True&dayRange={dayRange}""")
        url = (f"""https://kite.trade/connect/login?api_key=48pj63ie6z60osq7&v=3&redirect_params={encodedParams}""")
        response = RedirectResponse(url=url)
        return response
    elif source == 'nsepy':
        dayRange = int(dayRange)
        df = store.getNSEPyFullPriceData(dayRange)
        store.writeToDB(df)
        return "Sucesss"

@app.get("/instruments")
def get_instruments():
    global kite
    res = store.getInstruments(kite)
    return res
