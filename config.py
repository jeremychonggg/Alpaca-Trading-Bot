import requests 
import os 
import json 
import pandas as pd
from tabulate import tabulate 

# Change directory to the address below 
os.chdir("D:\\SynologyDrive\Programming\AlpacaTradingBot")

# Set Alpaca Endpoint 
trading_endpoint = "https://paper-api.alpaca.markets"  # Update link when change to real account  
data_endpoint = "https://data.alpaca.markets/v1"

# load "key.txt" as json file
headers = json.loads(open("key.txt", 'r').read())  # Update "key.txt" when change to real account

# Set timeframe of data that we want to get 
timeframe = "5Min"  # Available Timeframe: '1Min', '5Min', '15Min', '1D' 

# Set bar data url  
bar_url = data_endpoint + "/bars/{}".format(timeframe)

# Set parameters to request bar data 
# alpaca.markets/docs/api-documentation/api-v2/market-data/bars/
params = {"symbols": "MSFT,AAPL",
          "limit": 200}  

# make request from Alpaca Bar Data URL 
r = requests.get(bar_url, headers=headers, params=params)  

data = r.json()

temp = data["MSFT"]

df = pd.DataFrame(temp)

print(tabulate(df, headers='keys', tablefmt='psql'))