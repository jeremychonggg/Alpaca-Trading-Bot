import requests 
import os 
import json
import pandas as pd

os.chdir("D:\\SynologyDrive\Programming\AlpacaTradingBot")

endpoint = "https://paper-api.alpaca.markets"
headers = json.loads(open("key.txt", 'r').read())

# https://alpaca.markets/docs/api-documentation/api-v2/positions/
def get_position(symbol=""):
    if len(symbol) > 1:
        positions_url = endpoint + "/v2/positions/{}".format(symbol)
    else:
        positions_url = endpoint + "/v2/positions"
    r = requests.get(positions_url, headers=headers)
    return r.json()


def close_position(symbol="", qty=0):
    if len(symbol) > 1:
        positions_url = endpoint + "/v2/positions/{}".format(symbol)
        params = {"qty": qty}
    else:
        positions_url = endpoint + "/v2/positions"
        params = {}
    r = requests.delete(positions_url, headers=headers, json=params)
    return r.json()


# https://alpaca.markets/docs/api-documentation/api-v2/account/
def get_account():
    account_url = endpoint + "/v2/account"
    r = requests.get(account_url, headers=headers)
    return r.json()

