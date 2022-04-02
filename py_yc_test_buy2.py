import time
import pyupbit
import pandas as pd

ACCESS = "Jm80IMD467bKOkDhys8cHN76zEoFqdak9q8zv1B7"
SECRET = "Ufthev19QdRSpVw1pdvCjwYxMixZo2g8wLvzVkSC"
BAL_COIN = 100000

# 60개
ticker_list_manual = ["BTC","ETH","BCH","AAVE","LTC","SOL","BSV","AVAX","AXS","ETC","BTG","STRK","WAVES","ATOM","NEO","DOT","LINK","REP","NEAR","QTUM","FLOW","GAS","OMG","SBD","WEMIX","TON","KAVA","XTZ","THETA","SAND","CELO","KNC","AQT","SRM","EOS","MANA","CBK","LSK","DAWN","MTL","ENJ","1INCH","SXP","MATIC","STX","STORJ","ARK","STRAX","ADA","HIVE","PLA","HUNT","MLK","ICX","BORA","ALGO","PUNDIX","BAT","XRP","IOTA"]

# 로그인
upbit = pyupbit.Upbit(ACCESS, SECRET)

def get_current_price(i):
    global upbit_tickers
    """현재가 조회"""
    ticker = upbit_tickers[i]
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

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


# 전체 코인 가져오기
# upbit_tickers = pyupbit.get_tickers("KRW")
upbit_tickers = ["KRW-" for i in range(len(ticker_list_manual))]
for i in range(len(ticker_list_manual)):
    upbit_tickers[i] += ticker_list_manual[i]
    # print(upbit_tickers[i])

# 전체 코인 개수 가져오기
total_num_coin = len(upbit_tickers)
# total_num_coin = 110
print(total_num_coin)

# 매수 (BAL_COIN 보다 적은 경우 그차액만큼만 매수)
for i in range(total_num_coin):
    current_price = get_current_price(i) * get_balance(ticker_list_manual[i])
    if current_price < BAL_COIN:
        upbit.buy_market_order(upbit_tickers[i], BAL_COIN - current_price)
        print(upbit_tickers[i] + " Buy: " + "{:>7,.0f}".format(BAL_COIN - current_price))

    time.sleep(0.1)
      
# upbit.buy_market_order("KRW-DOGE", 5000)     

print("Buy End")

