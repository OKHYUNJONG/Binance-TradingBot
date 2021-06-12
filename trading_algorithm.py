import numpy as np
import seaborn as sns
import pandas as pd
import datetime
import os
import order
import data
import slack
import sqlite3

from sklearn.metrics import mean_squared_error

from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.models import Sequential
from datetime import datetime

from binance.client import Client

api_key = ""
secret_key = ""

client = Client(api_key, secret_key)

#매수 주문 
def buy_bitcoin():
    symbol = 'BTCUSDT'
    quantity = '0.002'
    client.get_open_orders    
    orderId = order.long_position(quantity)
    slack.buy_alarm(data.btc_price())
    
#매도 주문
def sell_bitcoin():
    symbol = 'BTCUSDT'
    quantity = '0.001998'
    client.get_open_orders
    orderId = order.short_position(quantity)
    slack.sell_alarm(data.btc_price())

#LSTM모델 가격예측 
def predict_price():
    client.get_open_orders

    candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1MINUTE)

    price = np.array([float(candles[i][4]) for i in range(500)])
    time = np.array([int(candles[i][0]) for i in range(500)])
    t = np.array([datetime.fromtimestamp(time[i]/1000).strftime('%H:%M:%S') for i in range(500)])
    price = price.reshape(500,1)

    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()

    scaler.fit(price[:374])
    normalized_price = scaler.transform(price)
    df = pd.DataFrame(normalized_price.reshape(100,5),columns=['First','Second','Third','Fourth','Target'])

    x_train = df.iloc[:74, :4]
    y_train = df.iloc[:74, -1]
    x_test = df.iloc[75:99,:4]
    y_test = df.iloc[75:99,-1]
    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_test = np.array(x_test)
    y_test = np.array(y_test)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1],1))
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1],1))

    model = Sequential()

    model.add(LSTM(20, return_sequences=True, input_shape=(4,1)))
    model.add(LSTM(40, return_sequences=False))
    model.add(Dense(1, activation='linear'))
    model.compile(loss = 'mse', optimizer = 'rmsprop')

    model.summary()

    model.fit(x_train, y_train, batch_size = 5, epochs = 100)
    y_pred = model.predict(x_test)

    symbol = 'BTCUSDT'
    quantity = '0.002'
    client.get_open_orders

    order = False


    while True:
        price = client.get_recent_trades(symbol = symbol)
        candle = client.get_klines(symbol= symbol, interval = Client.KLINE_INTERVAL_1MINUTE)
        GR = []
        for i in range(496,500):
            candles = scaler.transform(np.array([float(candle[i][4])]).reshape(1,-1))
            GR.append(candles)
            

        normalized_GR = np.array(GR)
        model_feed = normalized_GR.reshape(1,4,1)
        
        if order == False and float(price[len(price)-1]['price'])<float(scaler.inverse_transform(model.predict(model_feed)[0])[0]):

            return 1  

        elif order == True and float(price[len(price)-1]['price'])-300>float(scaler.inverse_transform(model.predict(model_feed)[0])[0]):
            order = False
            return 0

           
        else:
            pass


#피보나치 지지 자리 매수  (역추세)
def fibonacci_buy():
    btc_price = data.btc_price()

    conn = sqlite3.connect('5m.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS candles \
    (no integar,open_time text, close_time text, open_price text, close_price text, high_price text, low_price text, volume text)")
    cur.execute("SELECT * FROM candles")
    row = cur.fetchall()

    open_price = row[499][3]

    conn.close()

    if float(btc_price) < (float(open_price) - 15) :
        downturn = True
    else:
        downturn = False

    conn2 = sqlite3.connect('15mfibonacci_price.db')
    cur2 = conn2.cursor()
    cur2.execute("CREATE TABLE IF NOT EXISTS price \
    (price text)")
    cur2.execute("SELECT * FROM price")
    row2 = cur2.fetchall()
    for i in range(0,7):
        if float(row2[i][0])- 30 < float(btc_price) and float(btc_price) < float(row2[i][0]) + 30:
            near_fibo1 = True
            break
        else:
            near_fibo1 = False

    conn2.close

    conn3 = sqlite3.connect('1hfibonacci_price.db')
    cur3 = conn3.cursor()
    cur3.execute("CREATE TABLE IF NOT EXISTS price \
    (price text)")
    cur3.execute("SELECT * FROM price")
    row3 = cur3.fetchall()
    for i in range(0,7):
        if float(row2[i][0])- 30 < float(btc_price) and float(btc_price) < float(row2[i][0]) + 30:
            near_fibo2 = True
            break
        else:
            near_fibo2 = False

    conn3.close

    conn4 = sqlite3.connect('4hfibonacci_price.db')
    cur4 = conn4.cursor()
    cur4.execute("CREATE TABLE IF NOT EXISTS price \
    (price text)")
    cur4.execute("SELECT * FROM price")
    row4 = cur4.fetchall()
    for i in range(0,7):
        if float(row2[i][0])- 30 < float(btc_price) and float(btc_price) < float(row2[i][0]) + 30:
            near_fibo3 = True
            break
        else:
            near_fibo3 = False

    conn4.close

    if downturn == True and (near_fibo1 == True or near_fibo2 == True or near_fibo3 == True):
        return 1
    else:
        return 0 

#RSI 바닥 매수  (역추세)

def RSI_buy():
    RSI1 = data.get_RSI('5m')
    RSI2 = data.get_RSI('15m')
    RSI3 = data.get_RSI('1h')
    RSI4 = data.get_RSI('4h')
    if RSI1 <30 and RSI2 <35 and (RSI3< 50 or RSI4 < 50):
        return 1
    else:
        return 0


#RSI 정상화 매도 (단타)

def RSI_sell():
    RSI1 = data.get_RSI('5m')
    RSI2 = data.get_RSI('15m')
    RSI3 = data.get_RSI('1h')
    RSI4 = data.get_RSI('4h')
    if RSI1 >50 or RSI2 >40:
        return 1
    else:
        return 0

#단기 상승 매도

def Short_term_rise():
    btc_price = data.btc_price()

    conn = sqlite3.connect('5m.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS candles \
    (no integar,open_time text, close_time text, open_price text, close_price text, high_price text, low_price text, volume text)")
    cur.execute("SELECT * FROM candles")
    row = cur.fetchall()

    open_price = row[499][3]

    conn.close()

    if float(btc_price) > (float(open_price) + 500) :
        return 1
    else:
        return 0 

#손절
def sell_now():
    btc_price = data.btc_price()

    conn = sqlite3.connect('15m.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS candles \
    (no integar,open_time text, close_time text, open_price text, close_price text, high_price text, low_price text, volume text)")
    cur.execute("SELECT * FROM candles")
    row = cur.fetchall()

    open_price = row[499][3]

    conn.close()

    if float(btc_price) < (float(open_price) -500) :
        return 1
    else:
        return 0 
