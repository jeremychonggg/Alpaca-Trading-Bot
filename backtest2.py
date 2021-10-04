import requests 
import os 
import json
import pandas as pd 
from bs4 import BeautifulSoup
import requests 
from copy import deepcopy
import numpy as np
import alpaca_trade_api as tradeapi
import time 

endpoint = "https://data.alpaca.markets/v1"
headers = json.loads(open("key.txt", 'r').read())


# Webscrap list of top gainer stocks 
day_gainers_stock = {}
def find_day_gainers_stock():
    url = "https://finance.yahoo.com/gainers?count=100&offset=0" 
    page = requests.get(url)
    page_content = page.content
    soup = BeautifulSoup(page_content,'html.parser')
    table = soup.find_all("table", {"class" : "W(100%)"})
    for t in table:
        rows = t.find_all("tr")
        for row in rows:
            day_gainers_stock[row.get_text(separator='|').split("|")[0]] = row.get_text(separator='|').split("|")[4]


# Webscrap list of top volume stocks 
most_active_stock = {}
def find_most_active_stock():
    url = "https://finance.yahoo.com/most-active?count=100&offset=0" 
    page = requests.get(url)
    page_content = page.content
    soup = BeautifulSoup(page_content,'html.parser')
    table = soup.find_all("table", {"class" : "W(100%)"})
    for t in table:
        rows = t.find_all("tr")
        for row in rows:
            most_active_stock[row.get_text(separator='|').split("|")[0]] = row.get_text(separator='|').split("|")[5]





########## ENTRY STRATEGY - PREPARE LIST ##########
# Sort out 25 Top Gainer Stock from last trading day 
find_day_gainers_stock()  # Call this function on Monday 1 hour before market start 
# Sort out 25 Highest Volume Stock from last trading day 
find_most_active_stock()  # Call this function on Monday 1 hour before market start 


########## ENTRY STRATEGY - PICK TIMING ##########


########## BACKTESTING - PREPARE TOOLS ##########
def hist_data(symbols, timeframe="15Min", limit=200, start="", end="", after="", until=""):
    """
    Returns historical bar data for a string of symbols seperated by comma.
    Symbols should be in a string format separated by comma e.g. symbols = "MSFT,AMZN,GOOG".
    """
    df_data = {}
    bar_url = endpoint + "/bars/{}".format(timeframe)
    params = {"symbols" : symbols, 
              "limit"   : limit,
              "start"   : start,
              "end"     : end,
              "after"   : after, 
              "until"   : until}
    r = requests.get(bar_url, headers=headers, params=params)
    json_dump = r.json()
    for symbol in json_dump:
        temp = pd.DataFrame(json_dump[symbol])
        temp.rename({"t": "time", 
                     "o": "open",
                     "h": "high",
                     "l": "low",
                     "c": "close",
                     "v": "volume"}, axis=1, inplace=True)
        temp["time"] = pd.to_datetime(temp["time"], unit="s")
        temp.set_index("time", inplace=True)
        temp.index = temp.index.tz_localize("UTC").tz_convert("America/New_York")
        temp.between_time("09:31", "16:00")
        df_data[symbol] = temp
    
    return df_data

def MACD(df_dict, a=12, b=26, c=9):
    """
    function to calculate MACD 
    typical values: a(fast moving average) = 12;
                    b(slow moving average) = 26;
                    c(signal line ma window) = 9
    """
    for df in df_dict:
        df_dict[df]["ma_fast"] = df_dict[df]["close"].ewm(span=a, min_periods=a).mean()
        df_dict[df]["ma_slow"] = df_dict[df]["close"].ewm(span=b, min_periods=b).mean()
        df_dict[df]["macd"] = df_dict[df]["ma_fast"] - df_dict[df]["ma_slow"]
        df_dict[df]["signal"] = df_dict[df]["macd"].ewm(span=c, min_periods=c).mean()
        df_dict[df].drop(["ma_fast", "ma_slow"], axis=1, inplace=True)

def stochastic(df_dict, lookback=14, k=3, d=3):
    """
    function to calculate Stochastic Oscillator
    lookback = lookback period 
    k and d = moving average window for %K and %D
    """
    for df in df_dict:
        df_dict[df]["HH"] = df_dict[df]["high"].rolling(lookback).max()
        df_dict[df]["LL"] = df_dict[df]["low"].rolling(lookback).min()
        df_dict[df]["%K"] = (100 * (df_dict[df]["close"] - df_dict[df]["LL"]) / (df_dict[df]["HH"] - df_dict[df]["LL"])).rolling(k).mean()
        df_dict[df]["%D"] = df_dict[df]["%K"].rolling(d).mean()
        df_dict[df].drop(["HH", "LL"], axis=1, inplace=True)

# KPI 
def CAGR(df_dict, candle_period='1day'):
    "function to calculate the Cumulative Annual Growth Rate; DF should have return column"
    absolute_return = (1 + df_dict["return"]).cumprod().iloc[-1]

    if candle_period == '1day': 
        n = len(df_dict["return"]) / 252
    elif candle_period == '1hour':
        n = len(df_dict["return"]) / (252 * 8) 
    elif candle_period == '30min':
        n = len(df_dict["return"]) / (252 * 8 * 2) 
    elif candle_period == '15min':
        n = len(df_dict["return"]) / (252 * 8 * 4) 
    elif candle_period == '5min':
        n = len(df_dict["return"]) / (252 * 8 * 12) 
    elif candle_period == '3min':
        n = len(df_dict["return"]) / (252 * 8 * 20) 
    elif candle_period == '1min':
        n = len(df_dict["return"]) / (252 * 8 * 60) 
    
    cagr = (absolute_return)**(1/n) - 1

    # abs_return = (1 + df_dict["return"]).cumprod().iloc[-1]
    # n = len(df_dict[df])/252
    # cagr[df] = (abs_return)**(1/n) - 1

    # for df in df_dict:
        # abs_return = (1 + df_dict[df]["return"]).cumprod().iloc[-1]
        # n = len(df_dict[df])/252
        # cagr[df] = (abs_return)**(1/n) - 1

    return cagr

def volatility(df_dict):
    "function to calculate annualized volatility; DF should have ret column"
    vol = {}
    for df in df_dict:
        vol[df] = df_dict[df]["return"].std() * np.sqrt(252)
    return vol

def sharpe(df_dict, rf_rate):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    sharpe = {}
    cagr = CAGR(df_dict)
    vol = volatility(df_dict)
    for df in df_dict:
        sharpe[df] = (cagr[df] - rf_rate)/vol[df]
    return sharpe

def max_dd(df_dict):
    "function to calculate max drawdown"
    max_drawdown = {}
    for df in df_dict:
        df_dict[df]["cum_return"] = (1 + df_dict[df]["return"]).cumprod()
        df_dict[df]["cum_max"] = df_dict[df]["cum_return"].cummax()
        df_dict[df]["drawdown"] = df_dict[df]["cum_max"] - df_dict[df]["cum_return"]
        df_dict[df]["drawdown_pct"] = df_dict[df]["drawdown"]/df_dict[df]["cum_max"]
        max_drawdown[df] = df_dict[df]["drawdown_pct"].max()
        df_dict[df].drop(["cum_return","cum_max","drawdown","drawdown_pct"], axis=1, inplace=True)
    return max_drawdown

# INTRADAY KPI 
def winRate(DF):
    """
    function to calculate win rate of intrady trading strategy
    """
    df = DF["return"]
    pos = df[df>1]
    neg = df[df<1]
    return (len(pos) / len(pos + neg)) * 100 

def meanReturnPerTrade(DF):
    df = DF["return"]
    df_temp = (df - 1).dropna()
    return df_temp[df_temp != 0].mean()

def meanReturnWinRate(DF):
    df = DF["return"] 
    df_temp = (df - 1).dropna()
    return df_temp[df_temp > 0].mean()

def meanReturnLostRate(DF):
    df = DF["return"] 
    df_temp = (df - 1).dropna()
    return df_temp[df_temp < 0].mean()

def maxConsecutiveLoss(DF):
    df = DF["return"]
    df_temp = df.dropna(axis=0)
    df_temp2 = np.where(df_temp < 1, 1, 0)
    count_consecutive = []
    seek = 0
    for i in range(len(df_temp2)):
        if df_temp2[i] == 0:
            seek = 0
        else:
            seek = seek + 1
            count_consecutive.append(seek)
    
    if len(count_consecutive) > 0:
        return max(count_consecutive)
    else:
        return 0



########## BACKTESTING - START ##########
# Prepare tickers list 
tickers = ""
for ticker in most_active_stock:
    tickers = tickers + "," + ticker
tickers = tickers[8:]  # Remove the words ",symbol,"

# Get Historical Data 
historicalData = hist_data(tickers, limit=1000)

ohlc_dict = deepcopy(historicalData)
stoch_signal = {}
tickers_signal = {}
tickers_return = {}
trade_count = {}
trade_data = {}
high_water_mark = {}
# avg_return =  0  #

MACD(ohlc_dict)
stochastic(ohlc_dict)

for ticker in tickers.split(","):
    ohlc_dict[ticker].dropna(inplace=True)
    stoch_signal[ticker] = ""
    tickers_signal[ticker] = ""
    trade_count[ticker] = 0 
    high_water_mark[ticker] = 0
    tickers_return[ticker] = [0]
    trade_data[ticker] = {}

# Calculate Return of each stock 
for ticker in tickers.split(","):
    print("Calculation returns for:", ticker)
    for i in range(1, len(ohlc_dict[ticker])-1):
        # Strategy 1: Check Stochastic 
        if ohlc_dict[ticker]["%K"][i] < 20:
            stoch_signal[ticker] = "oversold"
        elif ohlc_dict[ticker]["%K"][i] > 80:
            stoch_signal[ticker] = "overbought"
        
        # ENTRY STRATEGY 
        if tickers_signal[ticker] == "":
            tickers_return[ticker].append(0)
            # LONG STRATEGY 
            if ( ohlc_dict[ticker]["macd"][i] > ohlc_dict[ticker]["signal"][i] ) and \
            ( ohlc_dict[ticker]["macd"][i-1] > ohlc_dict[ticker]["signal"][i-1] ) and \
            stoch_signal[ticker] == "oversold": 
                tickers_signal[ticker] = "Buy" 
                trade_count[ticker] += 1
                trade_data[ticker][trade_count[ticker]] = [ohlc_dict[ticker]["open"][i+1]]
                high_water_mark[ticker] = ohlc_dict[ticker]["open"][i+1]
        
        # EXIT STRATEGY 
        elif tickers_signal[ticker] == "Buy":
            # Check if stop loss triggered
            if ohlc_dict[ticker]["low"][i] < 0.985 * high_water_mark[ticker]:
                tickers_signal[ticker] = ""
                trade_data[ticker][trade_count[ticker]].append(0.985*high_water_mark[ticker])
                tickers_return[ticker].append( (0.985*high_water_mark[ticker] / ohlc_dict[ticker]["close"][i-1]) - 1 )
                trade_count[ticker] += 1 
            else:
                high_water_mark[ticker] = max(high_water_mark[ticker], ohlc_dict[ticker]["high"][i])
                tickers_return[ticker].append( (ohlc_dict[ticker]["close"][i] / ohlc_dict[ticker]["close"][i-1]) - 1 )

    if trade_count[ticker] % 2 != 0:
        trade_data[ticker][trade_count[ticker]].append(ohlc_dict[ticker]["close"][i+1])

    tickers_return[ticker].append(0)
    ohlc_dict[ticker]["return"] = np.array(tickers_return[ticker])
    # print(ohlc_dict[ticker]["return"][-1] * 100)  # print(ohlc_dict[ticker]["return"].sum() * 100)  #
    # avg_return = avg_return + (ohlc_dict[ticker]["return"].sum() * 100)  #
    # print(avg_return)  #

# Calculate Overall Stategy's KPI 
strategy_df = pd.DataFrame()
for ticker in tickers.split(","):
    strategy_df[ticker] = ohlc_dict[ticker]["return"]
    strategy_df[ticker].fillna(0, inplace=True)

strategy_df["return"] = strategy_df.mean(axis=1)

print("CAGR:", CAGR(strategy_df, candle_period='15min'))
# sharpe(strategy_df, 0.03)
# max_dd(strategy_df)


(1 + strategy_df["return"]).cumprod().plot()


