from binance.client import Client
from binance.websockets import BinanceSocketManager
import pandas as pd
import numpy as np
import requests 
import json
import sqlite3
import data

api_key = ""
api_secret = ""
client = Client(api_key, api_secret)




# 롱,숏 진입
from binance.enums import *

def long_position(q):
    order = client.order_market_buy(symbol='BTCUSDT', quantity=q)
    price = data.btc_price()

    conn = sqlite3.connect('buy_record.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS buy \
    (symbol text, entry_price text, quantity text, side text)")



    query = 'INSERT INTO buy VALUES(:symbol, :entry_price, :quantity, :side)'
    parameters = {
        "symbol": order['symbol'],
        "entry_price":price,
        "quantity":order['origQty'],
        "side":order['side']
    }
    cur.execute(query,parameters)
    conn.commit()

    conn.close()



def short_position(q):
    order = client.order_market_sell(symbol='BTCUSDT', quantity=q)
    price = data.btc_price()

    conn = sqlite3.connect('buy_record.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS buy \
    (symbol text, entry_price text, quantity text, side text)")



    query = 'INSERT INTO buy VALUES(:symbol, :entry_price, :quantity, :side)'
    parameters = {
        "symbol": order['symbol'],
        "entry_price":price,
        "quantity":order['origQty'],
        "side":order['side']
    }
    cur.execute(query,parameters)
    conn.commit()

    conn.close()


# 주문 상태 확인 
def order_state(order_Id):
    order = client.get_order(
        symbol='BTCUSDT',
        orderId=order_Id)
    return order

#주문 취소
def order_cancel(order_Id):
    result = client.cancel_order(
        symbol='BTCUSDT',
        orderId=order_Id)  

