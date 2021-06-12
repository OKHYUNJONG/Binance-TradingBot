from binance.client import Client
from binance.websockets import BinanceSocketManager
import pandas as pd
import numpy as np
import datetime
import requests 
import json
import sqlite3

api_key = ""
api_secret = ""
client = Client(api_key, api_secret)

#DB row count (테이블이 buy인 경우)
def row_count(db_address):
    conn = sqlite3.connect(db_address)
    cur = conn.cursor()
    cur.execute("SELECT * FROM buy")
    run = True
    i = 0
    while run:
        row = cur.fetchone()
        if row == None:
            run = False
            break

        i = i +1
    
    conn.close()
    return i

#서버시간 조회
def servertime():
    time_res = client.get_server_time()
    date = datetime.datetime.fromtimestamp(time_res["serverTime"]/1000)
    return date

#비트코인 현재가격 조회
def btc_price():
    price = client.get_symbol_ticker(symbol="BTCUSDT")
    return (price["price"])

#잔고 조회
def check_balance():
    balance = client.get_asset_balance(asset='USDT')
    total = float(balance["free"]) + float(balance["locked"])
    return total



#캔들 데이터 조회 (n분 봉) (가격/거래량) (최근 500개 불러옴)
def get_candle_data(time):
    time_min = time
    #ex) time_min = '5m'
    url = 'https://api.binance.com/api/v1/klines?symbol=BTCUSDT&interval='+time_min
    data = requests.get(url).json()
    #DB 생성 및 초기화
    conn = sqlite3.connect(time + '.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS candles \
    (no integar,open_time text, close_time text, open_price text, close_price text, high_price text, low_price text, volume text)")
    cur.execute("DELETE FROM candles;")
    conn.commit()

    for i in range(0,500):
        time_res = data[i][0]
        time_res2 = data[i][6]
        open = data[i][1]
        high = data[i][2]
        low = data[i][3]
        close = data[i][4]
        volume = data[i][5]
        open_time = datetime.datetime.fromtimestamp(time_res/1000)
        close_time = datetime.datetime.fromtimestamp(time_res2/1000)
        #DB에 값 전달 
        query = 'INSERT INTO candles VALUES(:no, :open_time, :close_time, :open_price, :close_price, :high_price, :low_price, :volume)'
        parameters = {
            "no": i,
            "open_time":open_time,
            "close_time":close_time,
            "open_price":open,
            "close_price":close,
            "high_price":high,
            "low_price":low,
            "volume":volume
        }
        cur.execute(query,parameters)
        conn.commit()
    conn.close()




#피보나치 지지/저항 가격 조회
def get_fibonacci_price(time):
    time_min = time
    #ex) time_min = '5m'

    #DB에서 값 불러오기
    conn = sqlite3.connect(time + '.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS candles \
    (no integar,open_time text, close_time text, open_price text, close_price text, high_price text, low_price text, volume text)")
    cur.execute("SELECT * FROM candles")
    row = cur.fetchall()


    Max_price = row[0][5]
    Min_price = row[0][6]
    for i in range(0,500):
        if(float(Max_price) < float(row[i][5])):
            Max_price = row[i][5]
        if(float(Min_price) > float(row[i][6])):
            Min_price = row[i][6]


    conn.close()  

    fibo0 = float(Min_price) + (float(Max_price) - float(Min_price)) * 0
    fibo1 = float(Min_price) + (float(Max_price) - float(Min_price)) * 0.236
    fibo2 = float(Min_price) + (float(Max_price) - float(Min_price)) * 0.382
    fibo3 = float(Min_price) + (float(Max_price) - float(Min_price)) * 0.5
    fibo4 = float(Min_price) + (float(Max_price) - float(Min_price)) * 0.618
    fibo5 = float(Min_price) + (float(Max_price) - float(Min_price)) * 0.786
    fibo6 = float(Min_price) + (float(Max_price) - float(Min_price)) * 1

    conn2 = sqlite3.connect(time + 'fibonacci_price.db')
    cur2 = conn2.cursor()
    cur2.execute("CREATE TABLE IF NOT EXISTS price \
    (price text)")
    cur2.execute("DELETE FROM price;")
    conn2.commit()

    query = 'INSERT INTO price VALUES(:price)'
    cur2.execute(query,{"price":fibo0})
    conn2.commit()
    cur2.execute(query,{"price":fibo1})
    conn2.commit()
    cur2.execute(query,{"price":fibo2})
    conn2.commit()
    cur2.execute(query,{"price":fibo3})
    conn2.commit()
    cur2.execute(query,{"price":fibo4})
    conn2.commit()
    cur2.execute(query,{"price":fibo5})
    conn2.commit()
    cur2.execute(query,{"price":fibo6})
    conn2.commit()

    conn2.close()

    

#RSI 수치 조회 
def get_RSI(time):

    conn = sqlite3.connect(time + '.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS candles \
    (no integar,open_time text, close_time text, open_price text, close_price text, high_price text, low_price text, volume text)")
    cur.execute("SELECT * FROM candles")
    row = cur.fetchall()
    AU = 0
    AD = 0
    i = 0
    j = 0
    for i in range(486,500):
        if(float(row[i][4]) > float(row[i-1][4])): #상승
            a = float(row[i][4]) - float(row[i-1][4])
            AU = AU + a
        elif(float(row[i][4]) < float(row[i-1][4])): #하락
            a = float(row[i-1][4]) - float(row[i][4])
            AD = AD + a
        else:
            a = 0
    RS = AU/AD
    RSI = RS/(1+RS)
    conn.close()

    return RSI


