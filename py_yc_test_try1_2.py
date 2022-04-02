from glob import glob
import time
from tkinter.messagebox import NO
import pyupbit
import pandas as pd
import datetime as dt

RATE_SELL_TH = 0.25
RATE_BUY_TH = 0.25
RATE_SELL_TRY = 1 + (RATE_SELL_TH/100) # 매도 기준
RATE_BUY_TRY = 1 - (RATE_BUY_TH/100) # 매수조건
UNIT_TRADE = 10000

ACCESS = "Jm80IMD467bKOkDhys8cHN76zEoFqdak9q8zv1B7"
SECRET = "Ufthev19QdRSpVw1pdvCjwYxMixZo2g8wLvzVkSC"
# ACCESS = "Jm80IMD467bKOkDhys8cHN76zEoFqdak9q8zv1B7"
# SECRET = "Ufthev19QdRSpVw1pdvCjwYxMixZo2g8wLvzVkSC"
INTERVAL_SEC = 0.1

# 50개
# ticker_list_manual = ["BTC","ETH","BCH","AAVE","LTC","SOL","BSV","AVAX","AXS","STRK","BTG","WAVES","ATOM","ETC","NEO","DOT","REP","LINK","NEAR","QTUM","FLOW","WEMIX","GAS","SBD","OMG","TON","KAVA","XTZ","SAND","THETA","KNC","AQT","MANA","CBK","LSK","EOS","SRM","DAWN","MTL","MATIC","1INCH","ENJ","STX","SXP","STORJ","STRAX","HIVE","ARK","BORA","ADA"]
# 60개
ticker_list_manual = ["BTC","ETH","BCH","AAVE","LTC","SOL","BSV","AVAX","AXS","ETC","BTG","STRK","WAVES","ATOM","NEO","DOT","LINK","REP","NEAR","QTUM","FLOW","GAS","OMG","SBD","WEMIX","TON","KAVA","XTZ","THETA","SAND","CELO","KNC","AQT","SRM","EOS","MANA","CBK","LSK","DAWN","MTL","ENJ","1INCH","SXP","MATIC","STX","STORJ","ARK","STRAX","ADA","HIVE","PLA","HUNT","MLK","ICX","BORA","ALGO","PUNDIX","BAT","XRP","IOTA"]

# 로그인
upbit = pyupbit.Upbit(ACCESS, SECRET)

start_total_coin_balance = 0
cash_balance_real = 0 # 현금잔고_실제
total_balance = 0 # 총잔고 (현금+코인)
cnt_sell = 0
cnt_buy = 0

def adjust_unit_price(price):
    # 코인 가격별 호가 단위
    if   (price >= 1) and (price < 10):             unit_coin = 0.01
    elif (price >= 10) and (price < 100):           unit_coin = 0.1
    elif (price >= 100) and (price < 1000):         unit_coin = 1
    elif (price >= 1000) and (price < 10000):       unit_coin = 5
    elif (price >= 10000) and (price < 100000):     unit_coin = 10
    elif (price >= 100000) and (price < 500000):    unit_coin = 50
    elif (price >= 500000) and (price < 1000000):   unit_coin = 100
    elif (price >= 1000000) and (price < 2000000):  unit_coin = 500
    elif (price >= 2000000):                        unit_coin = 1000
    elif (price >= 0.1) and (price < 1):            unit_coin = 0.001
    elif (price < 0.1):                             unit_coin = 0.0001
    
    # 호가 단위에 근접한 가격으로 설정
    x = price # 임력 금액
    b = unit_coin # 최소 단위
    a=0
    while a < x:
        c = a
        a += b
    bc=x-c
    ba=a-x
    if bc<ba:
        minn=c
    else:
        minn=a
    # 최소 호가 단위에 가까운 값으로 리턴
    return float(minn)

def get_current_price(i):
    global upbit_tickers
    """현재가 조회"""
    ticker = upbit_tickers[i]
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def buy_coin_reserv(_i, _target_price, _volume):
    global upbit_tickers
    ret = upbit.buy_limit_order(upbit_tickers[_i], _target_price, _volume)
    if ret != None:
        return ret['uuid']
    else:
        print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"buy_coin_reserv() - None: ret = upbit.buy_limit_order"+" {:<6s}".format(ticker_list[i])+" {:>7,.0f}".format(_target_price))
        return 'Nothing'
        
def sell_coin_reserv(_i, _target_price, _volume):
    global upbit_tickers
    ret = upbit.sell_limit_order(upbit_tickers[_i], _target_price, _volume)
    if ret != None:
        return ret['uuid']
    else:
        print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"sell_coin_reserv() - None: ret = upbit.sell_limit_order"+" {:<6s}".format(ticker_list[i])+" {:>7,.0f}".format(_target_price))
        return 'Nothing'
        
def get_balance(ticker):
    global upbit
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

now = dt.datetime.now()

# 전체 코인 가져오기
# upbit_tickers = pyupbit.get_tickers("KRW")
upbit_tickers = ["KRW-" for i in range(len(ticker_list_manual))]
for i in range(len(ticker_list_manual)):
    upbit_tickers[i] += ticker_list_manual[i]
    
# 전체 코인 개수 가져오기
total_num_coin = len(upbit_tickers)
print(now.strftime("%y%m%d %H:%M:%S"),"Coin number: {:>7,.0f}".format(total_num_coin))

# 전체 코인을 돌면서 'KRW-' 제외한 부분을 저장  upbit_tickers -> ticker_list
ticker_list = [0 for i in range(total_num_coin)]
for i in range(total_num_coin):
    ticker_list[i] = upbit_tickers[i][4:]

# 코인 개수 만큼의 리스트 사이즈 정의
start_coin_price = [0 for i in range(len(ticker_list))]
sell_target_price = [0 for i in range(len(ticker_list))]
buy_target_price = [0 for i in range(len(ticker_list))]
current_price_list = [0 for i in range(len(ticker_list))]
coin_number_list = [0 for i in range(len(ticker_list))]
start_coin_number = [0 for i in range(len(ticker_list))]
current_coin_price = [0 for i in range(len(ticker_list))]
current_coin_number = [0 for i in range(len(ticker_list))]
sell_volume_total = [0 for i in range(len(ticker_list))]
buy_volume_total = [0 for i in range(len(ticker_list))]
sell_volume = [0 for i in range(len(ticker_list))]
buy_volume = [0 for i in range(len(ticker_list))]
sell_cnt_weight = [0 for i in range(len(ticker_list))]
buy_cnt_weight = [0 for i in range(len(ticker_list))]

start_cash_balance = get_balance("KRW") # 시작시의 현금잔고

# 코인별 시작 기준가, 개수 저장
for i in range(len(ticker_list)):
    start_coin_price[i] = get_current_price(i)    # 초기 코인 시작가 저장
    start_coin_number[i] = get_balance(ticker_list[i])    # 초기 코인 개수 저장
    # 초기 코인 총자산(KRW) 계산
    start_total_coin_balance += (start_coin_price[i] * start_coin_number[i])
    
# 시작시 총 자산 = 시작시 현금가 + 시작시 총코인가
start_total_balance = start_cash_balance + start_total_coin_balance 

print(now.strftime("%y%m%d %H:%M:%S"),"Init End")
time.sleep(INTERVAL_SEC)

# Loop counter 초기화    
cnt_Tick = 0
step_coin = [1 for i in range(len(ticker_list))]    # 단계
coin_sell_uuid = ['Default' for i in range(len(ticker_list))]  # 코인 매도 UUID
coin_buy_uuid = ['Default' for i in range(len(ticker_list))]  # 코인 매수 UUID

# Loop 시작
print(now.strftime("%y%m%d %H:%M:%S"),"Loop Start")
while True:
    for i in range(len(ticker_list)):
        now = dt.datetime.now()
        cash_balance_real = get_balance("KRW")              # 현금 잔고 갱신
        coin_number_list[i] = get_balance(ticker_list[i])   # 코인 잔고 갱신
        current_price_list[i] = get_current_price(i)        # 코인 현재가 갱신
        
        if step_coin[i] == 1:
            
            step_coin[i] = 2 # STEP 증가
            sell_target_price[i] = adjust_unit_price(current_price_list[i] * RATE_SELL_TRY)
            sell_volume[i] = UNIT_TRADE*1.0005 / sell_target_price[i]
            buy_target_price[i] = adjust_unit_price(current_price_list[i] * RATE_BUY_TRY)
            buy_volume[i] = UNIT_TRADE / buy_target_price[i]
            # 1차 매도 주문
            if (coin_number_list[i] >= sell_volume[i]):
                coin_sell_uuid[i] = sell_coin_reserv(i, sell_target_price[i], sell_volume[i])
                sell_cnt_weight[i] = 0
            else:
                print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"Step1 매도 수량 부족"+"{:<6s}".format(ticker_list[i]) + "{:>7,.2f}".format(coin_number_list[i]) + "{:>7,.2f}".format(sell_volume[i]))
                step_coin[i] = 4 # STEP 증가
            # 1차 매수 주문
            if cash_balance_real > (UNIT_TRADE*1.0005):   
                coin_buy_uuid[i] = buy_coin_reserv(i, buy_target_price[i], buy_volume[i])
                buy_cnt_weight[i] = 0
            else:
                print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"Step1 매수 현금 부족"+"{:<6s}".format(ticker_list[i]) + "{:>7,.0f}".format(cash_balance_real) + "{:>7,.0f}".format(UNIT_TRADE*1.0005))
                step_coin[i] = 3 # STEP 증가
            
        elif step_coin[i] == 2:
            
            sell_order_status = upbit.get_order(coin_sell_uuid[i]) # 이전 매도 주문의 상태 확인
            buy_order_status = upbit.get_order(coin_buy_uuid[i]) # 이전 매수 주문의 상태 확인
            if sell_order_status != None:
                # 매도 체결 완료시
                if float(sell_order_status['remaining_volume']) == 0: # 기존 매도 체결 종료 여부 확인
                    sell_cnt_weight[i] += 1
                    cnt_sell += 1
                    print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"SELL done    " +"{:<6s}".format(ticker_list[i]) +"{:>7,.0f}".format(sell_target_price[i])+" Sell weight {:>2,.0f}".format(sell_cnt_weight[i]))
                    # 기존 매수주문 취소
                    if coin_buy_uuid[i] != 'Nothing':
                        upbit.cancel_order(coin_buy_uuid[i])
                    # 매수-> 매도
                    if buy_cnt_weight[i] > 0:
                        buy_cnt_weight[i] = 0
                        sell_volume_total[i] = 0
                        buy_volume_total[i] = 0
                        
                        buy_target_price[i] = adjust_unit_price(sell_target_price[i] * RATE_BUY_TRY)
                        buy_volume[i] = UNIT_TRADE / buy_target_price[i]
                        sell_target_price[i] = adjust_unit_price(sell_target_price[i] * RATE_SELL_TRY)
                        sell_volume[i] = UNIT_TRADE*1.0005 / sell_target_price[i]
                        # 다음 매도 주문
                        if (coin_number_list[i] >= sell_volume[i]):
                            coin_sell_uuid[i] = sell_coin_reserv(i, sell_target_price[i], sell_volume[i])
                            sell_cnt_weight[i] = 0
                        else:
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"Step2 매도 수량 부족"+"{:<6s}".format(ticker_list[i]) + "{:>7,.2f}".format(coin_number_list[i]) + "{:>7,.2f}".format(sell_volume[i]))
                            step_coin[i] = 4 # STEP 증가
                        # 다음 매수 주문
                        if cash_balance_real > (UNIT_TRADE*1.0005):   
                            coin_buy_uuid[i] = buy_coin_reserv(i, buy_target_price[i], buy_volume[i])
                            buy_cnt_weight[i] = 0
                        else:
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"Step2 매수 현금 부족"+"{:<6s}".format(ticker_list[i]) + "{:>7,.0f}".format(cash_balance_real) + "{:>7,.0f}".format(UNIT_TRADE*1.0005))
                            step_coin[i] = 3 # STEP 증가
                            
                    # 매도-> 매도
                    else:   
                        buy_volume_total[i] += sell_volume[i]
                        # 다음 매도 주문
                        sell_target_price[i] = adjust_unit_price( sell_target_price[i] * (RATE_SELL_TRY + (sell_cnt_weight[i]/1000)) )
                        sell_volume[i] = UNIT_TRADE*1.0005 / sell_target_price[i]
                        if (coin_number_list[i] >= sell_volume[i]):
                            coin_sell_uuid[i] = sell_coin_reserv(i, sell_target_price[i], sell_volume[i])
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"     order   " +"{:<6s}".format(ticker_list[i]) +"{:>7,.0f}".format(sell_target_price[i])+" Sell weight {:>2,.0f}".format(sell_cnt_weight[i]+1))
                        else:
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"Step2-1 매도 수량 부족"+"{:<6s}".format(ticker_list[i]) +"{:>7,.2f}".format(coin_number_list[i])+"{:>7,.2f}".format(sell_volume[i]))
                            step_coin[i] = 4
                        # 다음 매수 주문
                        if cash_balance_real > (buy_target_price[i] * buy_volume_total[i] * 1.0005):    
                            coin_buy_uuid[i] = buy_coin_reserv(i, buy_target_price[i], buy_volume_total[i])
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"     order   " +"{:<6s}".format(ticker_list[i]) +"{:>7,.0f}".format(buy_target_price[i])+" Buy weight  {:>2,.0f}".format(buy_cnt_weight[i]))
                        else:
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"Step2-1 매수 현금 부족"+"{:<6s}".format(ticker_list[i]) + " {:>7,.0f}".format(cash_balance_real) + " {:>7,.0f}".format(current_price_list[i] * buy_volume_total[i] * 1.0005))
                            step_coin[i] = 3 
            else:
                step_coin[i] = 1
                print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"매도 주문 없음: Move to Step1   " +"{:<6s}".format(ticker_list[i]))  
                
            if buy_order_status != None:    
                # 매수 체결 완료시
                if float(buy_order_status['remaining_volume']) == 0: # 기존 매수 체결 종료 여부 확인
                    buy_cnt_weight[i] += 1
                    cnt_buy += 1
                    print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"BUY* done    " +"{:<6s}".format(ticker_list[i]) +"{:>7,.0f}".format(buy_target_price[i])+" Buy weight {:>2,.0f}".format(buy_cnt_weight[i]))
                    # 기존 매도주문 취소
                    if coin_sell_uuid[i] != 'Nothing':
                        upbit.cancel_order(coin_sell_uuid[i])
                    # 매도-> 매수
                    if sell_cnt_weight[i] > 0:
                        sell_cnt_weight[i] = 0
                        sell_volume_total[i] = 0
                        buy_volume_total[i] = 0
                         
                        sell_target_price[i] = adjust_unit_price(buy_target_price[i] * RATE_SELL_TRY)
                        sell_volume[i] = UNIT_TRADE*1.0005 / sell_target_price[i]
                        buy_target_price[i] = adjust_unit_price(buy_target_price[i] * RATE_BUY_TRY)
                        buy_volume[i] = UNIT_TRADE / buy_target_price[i] * 2  # 최초 1회 매수는 2배 v1_2
                        # 다음 매도 주문
                        if (coin_number_list[i] >= sell_volume[i]):
                            coin_sell_uuid[i] = sell_coin_reserv(i, sell_target_price[i], sell_volume[i])
                            sell_cnt_weight[i] = 0
                        else:
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"Step1 매도 수량 부족"+"{:<6s}".format(ticker_list[i]) + "{:>7,.2f}".format(coin_number_list[i]) + "{:>7,.2f}".format(sell_volume[i]))
                            step_coin[i] = 4 # STEP 증가
                        # 다음 매수 주문
                        if cash_balance_real > (UNIT_TRADE*1.0005):   
                            coin_buy_uuid[i] = buy_coin_reserv(i, buy_target_price[i], buy_volume[i])
                            buy_cnt_weight[i] = 0
                        else:
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"Step1 매수 현금 부족"+"{:<6s}".format(ticker_list[i]) + "{:>7,.0f}".format(cash_balance_real) + "{:>7,.0f}".format(UNIT_TRADE*1.0005))
                            step_coin[i] = 3 # STEP 증가
                    # 매수-> 매수
                    else:
                        sell_volume_total[i] += buy_volume[i]
                        # 다음 매도 주문
                        if (coin_number_list[i] > sell_volume_total[i]):
                            coin_sell_uuid[i] = sell_coin_reserv(i, sell_target_price[i], sell_volume_total[i])
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"     order   " +"{:<6s}".format(ticker_list[i]) +"{:>7,.0f}".format(sell_target_price[i])+" Sell weight {:>2,.0f}".format(sell_cnt_weight[i]))
                        else:
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"Step2-2 매도 수량 부족"+" {:<6s}".format(ticker_list[i]) +" {:>7,.5f}".format(coin_number_list[i])+" {:>7,.5f}".format(sell_volume_total[i]))
                            sell_volume_total[i] = coin_number_list[i]
                            coin_sell_uuid[i] = sell_coin_reserv(i, sell_target_price[i], sell_volume_total[i])
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"     order   " +"{:<6s}".format(ticker_list[i]) +"{:>7,.0f}".format(sell_target_price[i])+" Sell weight {:>2,.0f}".format(sell_cnt_weight[i]))
                        # 다음 매수 주문
                        if cash_balance_real > (UNIT_TRADE*1.0005):
                            buy_target_price[i] = adjust_unit_price( buy_target_price[i] * (RATE_BUY_TRY - (buy_cnt_weight[i]/1000)) )
                            buy_volume[i] = UNIT_TRADE / buy_target_price[i]
                            coin_buy_uuid[i] = buy_coin_reserv(i, buy_target_price[i], buy_volume[i])
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"     order   " +"{:<6s}".format(ticker_list[i]) +"{:>7,.0f}".format(buy_target_price[i])+" Buy weight  {:>2,.0f}".format(buy_cnt_weight[i]+1))
                        else:
                            print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"Step2-2 매수 현금 부족"+" {:<6s}".format(ticker_list[i]) + "{:>7,.0f}".format(cash_balance_real) + " {:>7,.0f}".format(UNIT_TRADE*1.0005))
                            step_coin[i] = 3
            else:
                step_coin[i] = 1
                print("{:>4,d}".format(cnt_Tick),now.strftime("%y%m%d %H:%M:%S"),"BUY  Error (None-step2) : Move to Step1   " +"{:<6s}".format(ticker_list[i]))  

        elif step_coin[i] == 3:
            # 현금 부족시 여유 때 까지 기다린 후 Step 1로 이동
            if cash_balance_real > (UNIT_TRADE * 1.0005):
                step_coin[i] = 1
 
        elif step_coin[i] == 4:
            # 코인 부족시 여유 때 까지 기다린 후 Step 1로 이동
            if coin_number_list[i] >= sell_volume[i]:
                step_coin[i] = 1

    current_total_coin_balance = 0
    market_total_coin_balance = 0
    total_coin_number = 0
    current_total_balance = 0
    total_sell_cnt_weight = 0
    total_buy_cnt_weight = 0
    
    # 코인별 현재가, 개수 저장
    for i in range(len(ticker_list)):
        current_coin_price[i] = get_current_price(i) # 코인 현재가 저장
        current_coin_number[i] = get_balance(ticker_list[i]) # 코인 현재 개수 저장
        # 현재 코인 총자산(KRW) 계산
        current_total_coin_balance += (current_coin_price[i] * current_coin_number[i])
        # 시장 코인 총자산(KRW) 계산
        market_total_coin_balance += (current_coin_price[i] * start_coin_number[i])
        total_coin_number += current_coin_number[i] # 총 코인 개수 저장
        
        total_sell_cnt_weight += sell_cnt_weight[i]
        total_buy_cnt_weight += buy_cnt_weight[i]
        
    current_cash_balance = get_balance("KRW") # 현재 현금 저장
    # 현재 총 자산 = 현재 현금가 + 현재 총 코인가
    current_total_balance = current_cash_balance + current_total_coin_balance + (UNIT_TRADE* 1.0005*total_num_coin*2)
    # 시장 총 자산 = 초기 현금가 + (현재 코인가 x 초기 코인 개수)
    market_total_balance = start_cash_balance + market_total_coin_balance
    
    if cnt_Tick % 10 == 0:
        print("{:>4,d}".format(cnt_Tick), now.strftime("%y%m%d %H:%M:%S"),
            "Total: {:>7,.0f}".format(start_total_balance),"/ {:>7,.0f}".format(market_total_balance),"/ {:>7,.0f}".format(current_total_balance),
            " Cnt sell:{:>3,d}".format(cnt_sell),"/buy:{:>3,d}".format(cnt_buy),"  Weight sell:{:>3,d}".format(total_sell_cnt_weight),"/buy:{:>3,d}".format(total_buy_cnt_weight),"Total coin:{:>10,.3f}".format(total_coin_number))
    
    cnt_Tick += 1
