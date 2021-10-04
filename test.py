# Choose a Top Performer of ETF from previous week 
## https://www.etf.com/etfanalytics/etf-finder
etf_list = ['QQQ', 'QLD', 'TQQQ', 'GDXD', 'SPY']


# Get best ticker performance of past 1 week  
# def best_etf(etf_list):
#     best_ticker_performance = 0
#     best_ticker = ''

#     for ticker in etf_list:
#         ticker_yahoo = yf.Ticker(ticker)
#         data = ticker_yahoo.history()
#         last_quote = (data.tail(1)['Close'].iloc[0])
#         last_7th_quote = (data.tail(7)['Close'].iloc[0])  # 7 means last 7 days
#         last_week_performance = (last_quote - last_7th_quote) / last_7th_quote * 100

#         if last_week_performance > best_ticker_performance:
#             best_ticker_performance = last_week_performance 
#             best_ticker = ticker

#     return(best_ticker, round(best_ticker_performance, 2))

import json
import requests
import pandas as pd 

endpoint = "https://data.alpaca.markets/v1"
headers = json.loads(open("key.txt", 'r').read())

tickers = "ROXIF,EDU,TSP,PANW,PDD,BEKE,TAL,QFIN,TME,MPNGF,DADA,JD,DIDI,MPNGY,VNET,YY,ZH,YMM,BZ,CURV,FUTU,MLCO,TIGR,VIPS,FNMA"

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
        # temp.between_time("09:31", "16:00")
        df_data[symbol] = temp
    
    return df_data


historicalData = hist_data(tickers, timeframe="5Min")  

data_1h = {}
for ticker in historicalData:
    logic = {'open'  : 'first',
             'high'  : 'max',
             'low'   : 'min',
             'close' : 'last',
             'volume': 'sum'}
    data_1h[ticker] = historicalData[ticker].resample('1H').apply(logic)
    data_1h[ticker].dropna(inplace=True)

print(historicalData)