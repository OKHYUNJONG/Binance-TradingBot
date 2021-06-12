from slacker import Slacker

slack = Slacker('input your slacker')
# 슬랙에 매수/매도 시 알림 보내기
def buy_alarm(price):
    slack.chat.post_message('#coinorder', '비트코인 매수 진입 (진입가격:' + str(price) + ', 수량: 0.002)')

def sell_alarm(price):
    slack.chat.post_message('#coinorder', '비트코인 매도 진입 (진입가격:' + str(price) + ', 수량: 0.001998)')

