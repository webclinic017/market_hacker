from typing import Optional
from fastapi import FastAPI
from starlette.responses import RedirectResponse

import store

app = FastAPI()
kite = None
@app.get("/resetToken")
def read_root():
    pass


@app.get("/")
def read_root(request_token,load_data):
    kite = store.getKiteConnector(request_token)
    print(load_data)
    if  load_data == 'True':
        df = store.getFullPriceData(kite,5,'minute')
        store.writeToDB(df)
    return {"sucess": True}

@app.get("/stocks")
def read_root():
    res = store.getStockData()
    return res


@app.get("/loadData")
def load_data():
    url = ("https://kite.trade/connect/login?api_key=48pj63ie6z60osq7&v=3&redirect_params=load_data=True")
    response = RedirectResponse(url=url)
    return response



