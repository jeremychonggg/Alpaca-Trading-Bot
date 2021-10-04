To-Do List
1. Check 3 Methods of getting Historical Data 
https://www.udemy.com/course/algorithmic-trading-on-alpacas-platform-deep-dive/learn/lecture/26696542#overview
from main import bollinger_band, entry_strategy
import requests 
import os 
import json
import pandas as pd 

endpoint = "https://data.alpaca.markets/v2"
headers = json.loads(open("key.txt", 'r').read())

symbols = ["FB","CSCO","AMZN"]

def hist_data(symbols, start="2021-08-23", timeframe="1Day", limit=600, end=""):
    """
    returns historical bar data for a string of symbols separated by comma
    symbols should be in a string format separated by comma e.g. symbols = "MSFT,AMZN,GOOG"
    """
    df_data_tickers = {}
    
    for symbol in symbols:   
        bar_url = endpoint + "/stocks/{}/bars".format(symbol)
        params = {"start":start, "limit" :limit, "timeframe":timeframe}
        
        data = {"bars": [], "next_page_token":'', "symbol":symbol}
        while True:
                r = requests.get(bar_url, headers = headers, params = params)
                r = r.json()
                if r["next_page_token"] == None:
                    data["bars"]+=r["bars"]
                    break
                else:
                    params["page_token"] = r["next_page_token"]
                    data["bars"]+=r["bars"]
                    data["next_page_token"] = r["next_page_token"]
        
        # Create a DataFrame for the data["bars"] of each stock 
        df_data = pd.DataFrame(data["bars"])
        df_data.rename({"t":"time","o":"open","h":"high","l":"low","c":"close","v":"volume"},axis=1, inplace=True)
        df_data["time"] = pd.to_datetime(df_data["time"])
        df_data.set_index("time",inplace=True)
        df_data.index = df_data.index.tz_convert("America/Indiana/Petersburg")
        
        df_data_tickers[symbol] = df_data
    return data

print(hist_data(symbols))

# METHOD 1 OUTPUT 1: 
# {'bars': [{'t': '2021-08-25T04:00:00Z', 'o': 304.37, 'h': 304.59, 'l': 300.42, 'c': 302.01, 'v': 20496280, 'n': 226966, 'vw': 301.948381}], 'symbol': 'MSFT', 'next_page_token': None}

# METHOD 1 OUTPUT 2: 
# {'bars': [{'t': '2021-08-23T04:00:00Z', 'o': 303.245, 'h': 305.4, 'l': 301.85, 'c': 304.65, 'v': 22888060, 'n': 272839, 'vw': 304.280651}, 
#           {'t': '2021-08-24T04:00:00Z', 'o': 305.01, 'h': 305.65, 'l': 302.0035, 'c': 302.62, 'v': 18171043, 'n': 239227, 'vw': 303.090308}, 
#           {'t': '2021-08-25T04:00:00Z', 'o': 304.37, 'h': 304.59, 'l': 300.42, 'c': 302.01, 'v': 20496280, 'n': 226966, 'vw': 301.948381}], 
#  'symbol': 'MSFT', 
#  'next_page_token': None}

# METHOD 1 OUTPUT 3: 
# {'FB':                              open      high     low   close    volume       n          vw
# time
# 2021-08-23 00:00:00-04:00  359.15  365.6900  359.10  363.35  10926525  188923  363.749986
# 2021-08-24 00:00:00-04:00  363.89  367.9559  361.84  365.51   9232671  158006  365.715987
# 2021-08-25 00:00:00-04:00  365.91  370.8600  365.40  368.39   9679203  147499  368.524844, 
# 'CSCO':                             open   high      low  close    volume       n         vw
# time
# 2021-08-23 00:00:00-04:00  57.85  58.70  57.7435  58.54  16190458  104853  58.501415
# 2021-08-24 00:00:00-04:00  58.49  59.43  58.4300  59.32  17648835  108268  59.090894
# 2021-08-25 00:00:00-04:00  59.54  60.27  59.1700  59.35  18060523  114392  59.722240, 
# 'AMZN':                               open       high       low    close   volume       n           vw
# time
# 2021-08-23 00:00:00-04:00  3213.85  3280.9000  3210.005  3265.87  3269513  161814  3257.650270
# 2021-08-24 00:00:00-04:00  3281.00  3315.4942  3274.580  3305.78  2563649  146835  3299.813158
# 2021-08-25 00:00:00-04:00  3311.00  3321.0000  3286.150  3299.18  1678968  116032  3298.715197}

https://www.udemy.com/course/algorithmic-trading-quantitative-analysis-using-python/learn/lecture/19334304#overview
import datetime as dt
import yfinance as yf
import pandas as pd 

stocks = ["AMZN", "MSFT", "INTC"]
start = dt.datetime.today() - dt.timedelta(3)
end = dt.datetime.today() - dt.timedelta(1)

print(yf.download('AMZN', start, end))

# METHOD 2 OUTPUT 1:  
#                    Open         High          Low        Close    Adj Close   Volume
# Date
# 2021-08-23  3211.899902  3280.899902  3210.010010  3265.870117  3265.870117  3268100
# 2021-08-24  3280.000000  3315.489990  3274.580078  3305.780029  3305.780029  2551800


stocks = ["AMZN", "MSFT", "INTC"]
start = dt.datetime.today() - dt.timedelta(3)
end = dt.datetime.today() - dt.timedelta(1)
cl_price = pd.DataFrame()

for ticker in stocks:
    cl_price[ticker] = yf.download('AMZN', start, end)["Adj Close"]

print(cl_price)

# METHOD 2 OUTPUT 2: 
#                    AMZN         MSFT         INTC
# Date
# 2021-08-23  3265.870117  3265.870117  3265.870117
# 2021-08-24  3305.780029  3305.780029  3305.780029


https://www.udemy.com/course/algorithmic-trading-quantitative-analysis-using-python/learn/lecture/14558960#overview
import pandas as pd 
from yahoofinancials import YahooFinancials
import datetime as dt 

yahoo_financials = YahooFinancial("AAPL")
json_object = yahoo_financials.get_historical_price_data("2021-08-23", "2021-08-23", "daily")

print(json_object)

# METHOD 3 OUTPUT 1: 
#                              open      high     low   close    volume       n          vw
# time
# 2021-08-23 00:00:00-04:00  359.15  365.6900  359.10  363.35  10926525  188923  363.749986
# 2021-08-24 00:00:00-04:00  363.89  367.9559  361.84  365.51   9232671  158006  365.715987
# 2021-08-25 00:00:00-04:00  365.91  370.8600  365.40  368.39   9679203  147499  368.524844

import pandas as pd
from yfinance.tickers import Tickers 
from yahoofinancials import YahooFinancials
import datetime as dt 

tickers = ["AAPL", "MSFT", "CSCO"]

close_prices = pd.DataFrame()
for ticker in tickers:
    yahoo_financials = YahooFinancials(tickers)
    json_object = yahoo_financials.get_historical_price_data("2021-08-23", "2021-08-25", "daily")
    ohlv = json_object[ticker]['prices']
    temp = pd.DataFrame(ohlv)[["formatted_date", "adjclose"]]
    temp.set_index("formatted_date", inplace=True)
    temp.dropna(inplace=True)
    close_prices[ticker] = temp["adjclose"]

print(close_prices)

# METHOD 3 OUTPUT 2: 
#                       AAPL        MSFT       CSCO
# formatted_date
# 2021-08-23      149.710007  304.649994  58.540001
# 2021-08-24      149.619995  302.619995  59.320000

2. Store DataFrame of 3 Methods 

3. Compare DataFrame of 3 methods 
Method 1 (alpaca API)
Method 3 (https://pypi.org/project/yahoofinancials/)

4. Choose a way of doing General Trend (20EMA > 40EMA)


27-Aug (Fri)
5. Build bollinger_band()

6. Build rsi() 

7. Build entry_strategy()

8. Build open_long_position() 


[
    Position({   'asset_class': 'us_equity',
    'asset_id': '2d9e926c-e17c-47c3-ad8c-26c7a594e48f',
    'asset_marginable': True,
    'avg_entry_price': '375.41',
    'change_today': '0.0080285698942055',
    'cost_basis': '375.41',
    'current_price': '375.41',
    'exchange': 'NASDAQ',
    'lastday_price': '372.42',
    'market_value': '375.41',
    'qty': '1',
    'side': 'long',
    'symbol': 'QQQ',
    'unrealized_intraday_pl': '0',
    'unrealized_intraday_plpc': '0',
    'unrealized_pl': '0',
    'unrealized_plpc': '0'}), 
    Position({   'asset_class': 'us_equity',
    'asset_id': 'b0b6dd9d-8b9b-48a9-ba46-b9d54906e415',
    'asset_marginable': True,
    'avg_entry_price': '147.94',
    'change_today': '0.0029144638742036',
    'cost_basis': '147.94',
    'current_price': '147.97',
    'exchange': 'NASDAQ',
    'lastday_price': '147.54',
    'market_value': '147.97',
    'qty': '1',
    'side': 'long',
    'symbol': 'AAPL',
    'unrealized_intraday_pl': '0.03',
    'unrealized_intraday_plpc': '0.0002027849128025',
    'unrealized_pl': '0.03',
    'unrealized_plpc': '0.0002027849128025'})
]


9. Build open_short_position() 