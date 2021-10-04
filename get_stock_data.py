import json
import requests
import pandas as pd 
import websocket


# Get Alpaca API Credential
endpoint = "https://data.alpaca.markets/v2"
headers = json.loads(open("key.txt", 'r').read())



def hist_data(symbols, start="2021-01-01", timeframe="1Hour", limit=50, end=""):
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
        
        df_data = pd.DataFrame(data["bars"])
        df_data.rename({"t":"time","o":"open","h":"high","l":"low","c":"close","v":"volume"},axis=1, inplace=True)
        df_data["time"] = pd.to_datetime(df_data["time"])
        df_data.set_index("time",inplace=True)
        df_data.index = df_data.index.tz_convert("America/Indiana/Petersburg")
        
        df_data_tickers[symbol] = df_data
    return df_data_tickers
    

def get_historical_data(ticker_list, start_date, end_date=None, limit=10000, timeframe="1Day"):
    """
    returns historical bar data for a string of symbols separated by comma
    symbols should be in a string format separated by comma e.g. symbols = "MSFT,AMZN,GOOG"
    * timeframe - Timeframe for the aggregation. Available values are: `1Min`, `1Hour`, `1Day`
    
    https://alpaca.markets/docs/api-documentation/api-v2/market-data/alpaca-data-api-v2/historical/#bars
    """
    df_data_tickers = {}
    
    for symbol in ticker_list:
        bar_url = endpoint + "/stocks/{}/bars".format(symbol)
        params = {"start":start_date, "end": end_date, "limit": limit, "timeframe":timeframe}

        data = {"bars": [], "next_page_token": '', "symbol": symbol}

        # r = requests.get(bar_url, headers=headers, params=params)
        # r = r.json()
        # data["bars"] += r["bars"]
        while True:
            r = requests.get(bar_url, headers=headers, params=params)
            r = r.json()
            try:
                if r["next_page_token"] == None:
                    data["bars"] += r["bars"]
                    break
                else:
                    params["page_token"] = r["next_page_token"]
                    data["bars"] += r["bars"]
                    data["next_page_token"] = r["next_page_token"]
            except:
                break
        # Create a DataFrame for the data["bars"] of each stock 
        df_data = pd.DataFrame(data["bars"])
        df_data.rename({"t":"time","o":"open","h":"high","l":"low","c":"close","v":"volume"},axis=1, inplace=True)
        try:
            df_data["time"] = pd.to_datetime(df_data["time"])
            df_data.set_index("time",inplace=True)
            df_data.index = df_data.index.tz_convert("America/New_York")
            df_data_tickers[symbol] = df_data
        except:
            pass

        print("---- Created for [{}]".format(symbol))

    return df_data_tickers


