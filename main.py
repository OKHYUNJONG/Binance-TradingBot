import os
import sys
import data
import order
import trading_algorithm
import requests 
import json
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *




#main_ui실행

tickers = ["BTC/USDT"]
ui_path = os.path.dirname(os.path.abspath(__file__))
form_class = uic.loadUiType(os.path.join(ui_path, "main_ui.ui"))[0]

# 기본 정보


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pre_position.setRowCount(len(tickers))
        self.order = False

        self.get_candles_data()
        self.makeinit_db()
        #시작 시 잔고 금액 저장하기
        balance = data.check_balance()
        self.money.setItem(0, 1, QTableWidgetItem(str(balance)))
        
        #타이머 설정 (1-> 구매내역 갱신 , 2->n분봉 조회 , 3-> 5초마다 거래 만족여부 탐지, 4-> 200초마다 LSTM모델 예측)
        timer = QTimer(self)
        timer.start(1000)
        timer.timeout.connect(self.update_info)

        timer2 = QTimer(self)
        timer2.start(30000)
        timer2.timeout.connect(self.get_candles_data)

        timer3 = QTimer(self)
        timer3.start(5000)
        timer3.timeout.connect(self.start_trading)

        timer4 = QTimer(self)
        timer4.start(200000)
        timer4.timeout.connect(self.buy_algortihm_ML)



    def update_info(self): #실시간 정보 갱신 
        for i, ticker in enumerate(tickers):
            coin = QTableWidgetItem(ticker)
            self.pre_position.setItem(i, 0, coin)


        price = data.btc_price()
        time = data.servertime()
        totalvolume = data.check_balance()

        conn = sqlite3.connect('buy_record.db')
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS buy \
        (symbol text, entry_price text, quantity text, side text)")
        cur.execute("SELECT * FROM buy")
        num = data.row_count('buy_record.db')
        row = cur.fetchall()
        for i in range(0,num):
            entry_price = row[num-(i+1)][1]
            quantity = row[num-(i+1)][2]
            side = row[num-(i+1)][3]
            self.tradeview.setItem(i, 0, QTableWidgetItem(side))
            self.tradeview.setItem(i, 1, QTableWidgetItem(entry_price))
            self.tradeview.setItem(i, 2, QTableWidgetItem(str(quantity)))
        conn.close()

        self.pre_position.setItem(0, 1, QTableWidgetItem(str(price)))

        self.money.setItem(0, 0, QTableWidgetItem(str(totalvolume)))

        self.lineEdit.setText(str(time))

        

#30초 간격으로 DB 데이터 업데이트 (캔들, 피보나치)
    def get_candles_data(self):
        data.get_candle_data('1m')
        data.get_candle_data('5m')
        data.get_candle_data('15m')
        data.get_candle_data('1h')
        data.get_candle_data('4h')
        data.get_fibonacci_price('15m')
        data.get_fibonacci_price('1h')
        data.get_fibonacci_price('4h')


# 트레이딩 
    def start_trading(self):
        print("자동 거래 작동 중")
        # buy 알고리즘 구현 
        conn = sqlite3.connect('buy_algorithm1.db')
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS buy \
        (go integar)")
        cur.execute("SELECT * FROM buy")
        read_data =cur.fetchall()
        buy_algorithm1 = read_data[0][0]
        buy_algorithm2 = trading_algorithm.fibonacci_buy()
        buy_algorithm3 = trading_algorithm.RSI_buy()

        # sell 알고리즘 구현 
        sell_algorithm1 = trading_algorithm.Short_term_rise()
        sell_algorithm2 = trading_algorithm.RSI_sell()
        sell_algorithm3 = trading_algorithm.sell_now()
        

        #매수/메도 조건 만족 시 진행
        if buy_algorithm1 == 1 and buy_algorithm2 == 1 and buy_algorithm3 == 1 and self.order == False:
            orderId_buy = trading_algorithm.buy_bitcoin()
            self.order = True

        if (sell_algorithm1 == 1 or sell_algorithm2 == 1 or sell_algorithm3 == 1) and self.order == True:
            orderId_sell = trading_algorithm.sell_bitcoin()
            self.AllowNestedDocksorder = False

    # 200초에 한 번 분석
    def buy_algortihm_ML(self):
        conn = sqlite3.connect('buy_algorithm1.db')
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS buy \
        (go integar)")
        cur.execute("DELETE FROM buy;")
        conn.commit()
        buy_algorithm1 = trading_algorithm.predict_price()
        query = 'INSERT INTO buy VALUES(:go)'
        parameters = {"go": buy_algorithm1}
        cur.execute(query,parameters)
        conn.commit()
        conn.close()

    def makeinit_db(self):
        conn = sqlite3.connect('buy_algorithm1.db')
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS buy \
        (go integar)")
        cur.execute("DELETE FROM buy;")
        conn.commit()
        query = 'INSERT INTO buy VALUES(:go)'
        parameters = {"go": 0}
        cur.execute(query,parameters)
        conn.commit()
        conn.close()


app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()





