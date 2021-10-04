import alpaca_trade_api as tradeapi 
import os 
import json


os.chdir("D:\\SynologyDrive\Programming\AlpacaTradingBot")
headers = json.loads(open("key.txt", 'r').read())
key = json.loads(open("key.txt", "r").read())

api = tradeapi.REST(key["APCA-API-KEY-ID"], key["APCA-API-SECRET-KEY"], base_url="https://paper-api.alpaca.markets")


# Get account info 
account_info = api.get_account()
# account_info.equity


# Get position info 
position_list = api.list_positions()
# position_list[0]


# Get historical data 
data = api.get_barset("FB,CSCO,INTC", limit=100, timeframe="15Min")
# print(data["FB"][-1].c)

last_quote = api.get_last_quote("CSCO")
# print(last_quote)
# print(last_quote.askprice)


api.submit_order("GOOG", 1, "sell", "market", "day")
api.submit_order("CSCO", 10, "buy", "limit", "day", "44.8")
api.submit_order("FB", 10, "sell", "stop", "day", stop_price="271")
api.submit_order("GOOG", 10, "sell", "trailing_stop", "day", trail_price="3")
