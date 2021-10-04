import requests 
import os 
import json 
import pandas as pd 

os.chdir("D:\\SynologyDrive\Programming\AlpacaTradingBot")

endpoint = "https://paper-api.alpaca.markets"
headers = json.loads(open("key.txt", 'r').read())

# https://alpaca.markets/docs/api-documentation/api-v2/orders/
def market_order(symbol, quantity, side="buy", tif="day"):
    order_url = endpoint + "/v2/orders"
    params = {"symbol"        : symbol,
              "qty"           : quantity,  # Number of shares to trade 
              "side"          : side,  # 'buy' or 'sell'
              "type"          : "market",  # 'market', 'limit', 'stop', 'stop_limit', 'trailing_stop'
              "time_in_force" : tif  # 'day', 'gtc', 'opg', 'cls', 'ioc' or 'fok'
              }
    r = requests.post(order_url, headers=headers, json=params)
    return r.json()


def limit_order(symbol, quantity, limit_price, side="buy", tif="day"):
    order_url = endpoint + "/v2/orders"
    params = {"symbol"          : symbol,
              "qty"             : quantity,  # Number of shares to trade 
              "side"            : side,  # 'buy' or 'sell'
              "type"            : "limit",  # 'market', 'limit', 'stop', 'stop_limit', 'trailing_stop'
              "limit_price"     : limit_price,  # price to go in 
              "time_in_force"   : tif  # 'day', 'gtc', 'opg', 'cls', 'ioc' or 'fok'
              }
    r = requests.post(order_url, headers=headers, json=params)
    return r.json()


def stop_order(symbol, quantity, stop_price, side="buy", tif="day"):
    order_url = endpoint + "/v2/orders"
    params = {"symbol"          : symbol,
              "qty"             : quantity,  # Number of shares to trade 
              "side"            : side,  # 'buy' or 'sell'
              "type"            : "stop",  # 'market', 'limit', 'stop', 'stop_limit', 'trailing_stop'
              "stop_price"      : stop_price,
              "time_in_force"   : tif  # 'day', 'gtc', 'opg', 'cls', 'ioc' or 'fok'
              }
    r = requests.post(order_url, headers=headers, json=params)
    return r.json()


def stop_limit_order(symbol, quantity, stop_price, limit_price, side="buy", tif="day"):
    order_url = endpoint + "/v2/orders"
    params = {"symbol"          : symbol,
              "qty"             : quantity,  # Number of shares to trade 
              "side"            : side,  # 'buy' or 'sell'
              "type"            : "stop_limit",  # 'market', 'limit', 'stop', 'stop_limit', 'trailing_stop'
              "stop_price"      : stop_price,
              "limit_price"     : limit_price,
              "time_in_force"   : tif  # 'day', 'gtc', 'opg', 'cls', 'ioc' or 'fok'
              }
    r = requests.post(order_url, headers=headers, json=params)
    return r.json()


def trail_stop_order(symbol, quantity, trail_price, side="buy", tif="day"):
    order_url = endpoint + "/v2/orders"
    params = {"symbol"          : symbol,
              "qty"             : quantity,  # Number of shares to trade 
              "side"            : side,  # 'buy' or 'sell'
              "type"            : "trailing_stop",  # 'market', 'limit', 'stop', 'stop_limit', 'trailing_stop'
              "trail_price"     : trail_price,
              "time_in_force"   : tif  # 'day', 'gtc', 'opg', 'cls', 'ioc' or 'fok'
              }
    r = requests.post(order_url, headers=headers, json=params)
    return r.json()


def bracket_order(symbol, quantity, tp_limit_price, sl_stop_price, sl_limit_price, side="buy", tif="day"):
    order_url = endpoint + "/v2/orders"
    params = {"symbol"          : symbol,
              "qty"             : quantity,  # Number of shares to trade 
              "side"            : side,  # 'buy' or 'sell'
              "type"            : "market",  # 'market', 'limit', 'stop', 'stop_limit', 'trailing_stop'
              "time_in_force"   : tif,  # 'day', 'gtc', 'opg', 'cls', 'ioc' or 'fok'
              "order_class"     : "bracket",
              "take_profit"     : {"limit_price": tp_limit_price},
              "stop_loss"       : {"stop_price" : sl_stop_price, 
                                   "limit_price": sl_limit_price
                                   }
              }
    r = requests.post(order_url, headers=headers, json=params)
    return r.json()


def order_list(status="open", limit=50):
    """
    Retrieves a list of orders for the account, filtered by the supplied query parameters.
    """
    order_list_url = endpoint + "/v2/orders"
    params = {"status": status}
    r = requests.get(order_list_url, headers=headers, params=params)
    data = r.json()
    return pd.DataFrame(data)


def order_cancel(order_id=""):
    if len(order_id) > 1:
        # Cancel specific order 
        order_cancel_url = endpoint + "/v2/orders/{}".format(order_id)
    else: 
        # Cancel all order 
        order_cancel_url = endpoint + "/v2/orders"
    r = requests.delete(order_cancel_url, headers=headers)
    return r.json()

# order_df = order_list()
# order_cancel(order_df[order_df["symbol"]=="CSCO"]["id"].to_list()[0])


def order_replace(order_id, params):
    order_cancel_url = endpoint + "/v2/orders/{}".format(order_id)
    r = requests.patch(order_cancel_url, headers=headers, json=params)
    return r.json()

# order_replace(order_df[order_df["symbol"]=="CSCO"]["id"].to_list()[0],
#               {"qty": 10, "trail": 3})