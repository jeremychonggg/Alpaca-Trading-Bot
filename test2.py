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


print(YahooFinancials("AAPL").get_50day_moving_avg())
print(YahooFinancials("AAPL").get_200day_moving_avg())