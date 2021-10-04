# Import Modules
import json
import pandas as pd
import requests
from numpy import short
from strategies import exit_strategy
import alpaca_trade_api as tradeapi
import time 
import datetime as dt
from copy import deepcopy
import numpy as np

# Import Files 
from prepare_ticker_list import prepare_ticker_list
from get_stock_data import get_historical_data, hist_data
from indicators import general_trend, bollinger_band, rsi 


# Startup Configuration 
endpoint = "https://data.alpaca.markets/v2"
headers = json.loads(open("key.txt",'r').read())
api = tradeapi.REST(headers["APCA-API-KEY-ID"], headers["APCA-API-SECRET-KEY"], base_url='https://paper-api.alpaca.markets')


def remove_opened_position(pre_ticker_list, opened_position_ticker_list):
    """
    Return a list of tickers that do not have any position opened.
    """
    ticker_list = pre_ticker_list

    for pre_ticker in pre_ticker_list:
        for opened_position_ticker in opened_position_ticker_list:
            if pre_ticker == opened_position_ticker:
                ticker_list.remove(opened_position_ticker)
    
    return ticker_list


def exit_strategy(opened_position_dataframe, opened_position_list):
    # Add indicators into dataframe 
    ## Take Profit Bollinger Band
    bollinger_band(opened_position_dataframe, length=50, stdDev=1, name='TP')
    ## Stop Loss Bollinger Band
    bollinger_band(opened_position_dataframe, length=50, stdDev=6, name='SL')

    # Exit Strategy 
    for position in opened_position_list:
        print("---- Checking [{}]".format(position.symbol))

        symbol = position.symbol
        side = position.side
        entry_price = float(position.avg_entry_price)
        last_close = float(position.lastday_price)
        quantity_of_stock = float(position.qty)
        market_value = float(position.market_value)
        # print("TICKER:", symbol)
        # print("ENTRY PRICE:", entry_price)
        # print("SIDE:", side)

        # Long Exit Strategy 
        if side == 'long':
            take_profit = float(opened_position_dataframe[symbol]['BB_TP_UB'].iloc[-1]) 
            stop_loss = float(opened_position_dataframe[symbol]['BB_SL_LB'].iloc[-1]) 
            
            total_long_take_profit_cash_amount = take_profit * quantity_of_stock 
            total_long_stop_loss_cash_amount = stop_loss * quantity_of_stock

            if last_close >= take_profit:
                api.submit_order(symbol, quantity_of_stock, type='stop', time_in_force='day', stop_price=take_profit)
                print("------------------------------------------------------------")
                print(">>>>>>>>>>| OPEN STOP ORDER | LONG | TAKE PROFIT |<<<<<<<<<<") 
                print("TICKER:", symbol)
                print("LONG ENTRY PRICE: $", entry_price)
                print("LONG ENTRY QUANTITY:", quantity_of_stock)
                print("TOTAL ENTRY CASH AMOUNT: $", market_value)
                print("..................................................")
                print("LONG EXIT PRICE: $", take_profit)
                print("LONG EXIT QUANTITY:", quantity_of_stock)
                print("TOTAL EXIT CASH AMOUNT: $", total_long_take_profit_cash_amount)
                print("------------------------------------------------------------")

            elif last_close <= stop_loss:
                api.submit_order(symbol, quantity_of_stock, type='stop', time_in_force='day', stop_price=stop_loss)
                print("------------------------------------------------------------")
                print(">>>>>>>>>>| OPEN STOP ORDER | LONG | STOP LOSS |<<<<<<<<<<") 
                print("TICKER:", symbol)
                print("LONG ENTRY PRICE: $", entry_price)
                print("LONG ENTRY QUANTITY:", quantity_of_stock)
                print("TOTAL ENTRY CASH AMOUNT: $", market_value)
                print("..................................................")
                print("LONG EXIT PRICE: $", stop_loss)
                print("LONG EXIT QUANTITY:", quantity_of_stock)
                print("TOTAL EXIT CASH AMOUNT: $", total_long_stop_loss_cash_amount)
                print("------------------------------------------------------------") 

        # Short Exit Strategy 
        elif side == 'short':
            take_profit = float(opened_position_dataframe[symbol]['BB_TP_LB'].iloc[-1]) 
            stop_loss = float(opened_position_dataframe[symbol]['BB_SL_UB'].iloc[-1]) 

            total_short_take_profit_cash_amount = take_profit * quantity_of_stock 
            total_short_stop_loss_cash_amount = stop_loss * quantity_of_stock

            if last_close <= take_profit:
                api.submit_order(symbol, quantity_of_stock, type='stop', time_in_force='day', stop_price=take_profit)
                print("------------------------------------------------------------")
                print(">>>>>>>>>>| OPEN STOP ORDER | SHORT | TAKE PROFIT |<<<<<<<<<<") 
                print("TICKER:", symbol)
                print("LONG ENTRY PRICE: $", entry_price)
                print("LONG ENTRY QUANTITY:", quantity_of_stock)
                print("TOTAL ENTRY CASH AMOUNT: $", market_value)
                print("..................................................")
                print("LONG EXIT PRICE: $", take_profit)
                print("LONG EXIT QUANTITY:", quantity_of_stock)
                print("TOTAL EXIT CASH AMOUNT: $", total_short_take_profit_cash_amount)
                print("------------------------------------------------------------") 
            elif last_close >= stop_loss:
                api.submit_order(symbol, quantity_of_stock, type='stop', time_in_force='day', stop_price=stop_loss)
                print("-----------------------------------------------")
                print(">>>>>>>>>>| OPEN STOP ORDER | SHORT | STOP LOSS |<<<<<<<<<<") 
                print("TICKER:", symbol)
                print("SHORT ENTRY PRICE: $", entry_price)
                print("SHORT ENTRY QUANTITY:", quantity_of_stock)
                print("TOTAL ENTRY CASH AMOUNT: $", market_value)
                print("SHORT EXIT PRICE: $", stop_loss)
                print("SHORT EXIT QUANTITY:", quantity_of_stock)
                print("TOTAL EXIT CASH AMOUNT: $", total_short_stop_loss_cash_amount)
                print("-----------------------------------------------")


def entry_strategy(dataframe, ticker_list):
    # Add indicators into dataframe 
    ## Entry Bollinger Band 
    bollinger_band(dataframe, length=50, stdDev=2, name='E')
    ## Stop Loss Bollinger Band
    bollinger_band(dataframe, length=50, stdDev=6, name='SL')
    ## Entry RSI 
    rsi(dataframe, period=14)

    # Entry Strategy 
    for ticker in ticker_list:
        
        print("---- Checking [{}]".format(ticker))
        
        # Get Ticker Info 
        last_close = float(dataframe[ticker]['close'].iloc[-1]) 
        long_entry_price = float(dataframe[ticker]['BB_E_LB'].iloc[-1]) 
        short_entry_price = float(dataframe[ticker]['BB_E_UB'].iloc[-1]) 
        rsi_value = float(dataframe[ticker]['rsi'].iloc[-1]) 
        long_entry_temp_stop_loss_price = float(dataframe[ticker]['BB_SL_LB'].iloc[-1]) 
        short_entry_temp_stop_loss_price = float(dataframe[ticker]['BB_SL_UB'].iloc[-1]) 

        # Get Account Info 
        account_info = api.get_account()
        current_available_equity = round(float(account_info.equity), 2)
        current_available_cash = round(float(account_info.cash), 2)        
        
        # Set Risk Per Trade
        percentage_risk_per_trade = 0.01

        # Long Entry Strategy 
        if (last_close <= long_entry_price) and (rsi_value <= 40):
            # Prepare Order 
            risk_per_share = last_close - long_entry_temp_stop_loss_price
            quantity = (percentage_risk_per_trade * current_available_equity) / risk_per_share
            amount_to_open = last_close * quantity

            # Calculate if enough money to open position
            if (current_available_cash >= amount_to_open):
                api.submit_order(ticker, quantity, 'buy', 'limit', 'day', limit_price=long_entry_price)
                print("-----------------------------------------------")
                print(">>>>>>>>>>| OPEN LIMIT ORDER | LONG |<<<<<<<<<<") 
                print("TICKER:", ticker)
                print("LONG ENTRY PRICE: $", long_entry_price)
                print("LONG ENTRY QUANTITY:", quantity)
                print("TOTAL ENTRY CASH AMOUNT: $", amount_to_open)
                print("-----------------------------------------------")

        # Short Entry Strategy 
        elif (last_close >= short_entry_price) and (rsi_value >= 60):
            # Prepare Order 
            risk_per_share = short_entry_temp_stop_loss_price - last_close 
            quantity = (percentage_risk_per_trade * current_available_equity) / risk_per_share
            amount_to_open = last_close * quantity
            
            # Calculate if enough money to open position
            if (current_available_cash >= amount_to_open):
                print("------------------------------------------------")
                print(">>>>>>>>>>| OPEN LIMIT ORDER | SHORT |<<<<<<<<<<")  
                print("TICKER:", ticker)
                print("SHORT ENTRY PRICE: $", short_entry_price)
                print("SHORT ENTRY QUANTITY:", quantity)
                print("TOTAL ENTRY CASH AMOUNT: $", amount_to_open)
                print("------------------------------------------------")
                api.submit_order(ticker, quantity, 'sell', 'limit', 'day', limit_price=short_entry_price)


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



########## BACKTESTING - START ##########
# GET TICKER LIST
pre_ticker_list = prepare_ticker_list()
opened_position_list = api.list_positions()
opened_position_ticker_list = []
for position in opened_position_list:
    opened_position_ticker_list.append(position.symbol)
ticker_list = remove_opened_position(pre_ticker_list, opened_position_ticker_list)

# GET HISTORICAL DATA 
dataframe = get_historical_data(ticker_list, start_date='2021-07-01', limit=10000)

# CONFIGURATION 
current_available_equity = 10,000
ohlc_dict = deepcopy(dataframe)
rsi_signal = {}
tickers_signal = {}
tickers_return = {}
trade_count = {}
trade_data = {}
high_water_mark = {}

# Add indicators into dataframe 
## Entry Bollinger Band 
bollinger_band(dataframe, length=50, stdDev=2, name='E')
## Take Profit Bollinger Band
bollinger_band(dataframe, length=50, stdDev=1, name='TP')
## Stop Loss Bollinger Band
bollinger_band(dataframe, length=50, stdDev=6, name='SL')
## Entry RSI 
rsi(dataframe, period=14)

# Entry Strategy 
for ticker in ticker_list:
    ohlc_dict[ticker].dropna(inplace=True)
    rsi_signal[ticker] = ""
    tickers_signal[ticker] = ""
    trade_count[ticker] = 0 
    high_water_mark[ticker] = 0
    tickers_return[ticker] = [0]
    trade_data[ticker] = {}
    print("---- Checking [{}]".format(ticker))

    # Get Ticker Info 
    last_close = float(dataframe[ticker]['close'].iloc[-1]) 
    long_entry_price = float(dataframe[ticker]['BB_E_LB'].iloc[-1]) 
    short_entry_price = float(dataframe[ticker]['BB_E_UB'].iloc[-1]) 
    rsi_value = float(dataframe[ticker]['rsi'].iloc[-1]) 
    long_entry_temp_stop_loss_price = float(dataframe[ticker]['BB_SL_LB'].iloc[-1]) 
    short_entry_temp_stop_loss_price = float(dataframe[ticker]['BB_SL_UB'].iloc[-1]) 

    # Get Account Info 
    account_info = api.get_account()
    current_available_equity = round(float(account_info.equity), 2)
    current_available_cash = round(float(account_info.cash), 2)        
    
    # Set Risk Per Trade
    percentage_risk_per_trade = 0.01


for ticker in ticker_list:

    # Calculate Return of each stock 
    print("Calculation returns for:", ticker)
    for i in range(1, len(ohlc_dict[ticker])-1):

        # Get Ticker Info 
        last_close = float(dataframe[ticker]['close'].iloc[i]) 
        next_open = float(dataframe[ticker]['open'].iloc[i+1])
        long_entry_price = float(dataframe[ticker]['BB_E_LB'].iloc[i]) 
        short_entry_price = float(dataframe[ticker]['BB_E_UB'].iloc[i]) 
        rsi_value = float(dataframe[ticker]['rsi'].iloc[i]) 
        long_entry_take_profit_price = float(dataframe[ticker]['BB_TP_UB'].iloc[i]) 
        long_entry_stop_loss_price = float(dataframe[ticker]['BB_SL_LB'].iloc[i]) 
        short_entry_stop_loss_price = float(dataframe[ticker]['BB_SL_UB'].iloc[i]) 

        # Get Account Info 
        account_info = api.get_account()
        current_available_equity = round(float(account_info.equity), 2)
        current_available_cash = round(float(account_info.cash), 2)        
        
        # Set Risk Per Trade
        percentage_risk_per_trade = 0.01

        
        # ENTRY STRATEGY  
        if tickers_signal[ticker] == "":
            tickers_return[ticker].append(0)
            # LONG ENTRY STRATEGY 
            if (last_close <= long_entry_price) and (rsi_value <= 40): 
                tickers_signal[ticker] = "Buy" 
                trade_count[ticker] += 1
                trade_data[ticker][trade_count[ticker]] = float([ohlc_dict[ticker]["open"][i+1]])
                high_water_mark[ticker] = float(ohlc_dict[ticker]["open"][i+1])
        
        # EXIT STRATEGY 
        elif tickers_signal[ticker] == "Buy":
            # Check if stop loss triggered
            if last_close <= long_entry_stop_loss_price:
                tickers_signal[ticker] = ""
                trade_data[ticker][trade_count[ticker]].append(next_open)
                tickers_return[ticker].append( (next_open / last_close) - 1 )
                trade_count[ticker] += 1 
            # Check if take profit triggered 
            elif last_close >= long_entry_take_profit_price:
                high_water_mark[ticker] = max(float(high_water_mark[ticker]), float(ohlc_dict[ticker]["high"][i]))
                tickers_return[ticker].append( (next_open / last_close) - 1 )

    if trade_count[ticker] % 2 != 0:
        trade_data[ticker][trade_count[ticker]].append(float(ohlc_dict[ticker]["close"][i+1]))

    tickers_return[ticker].append(0)
    ohlc_dict[ticker]["return"] = np.array(tickers_return[ticker])
    # print(ohlc_dict[ticker]["return"][-1] * 100)  # print(ohlc_dict[ticker]["return"].sum() * 100)  #
    # avg_return = avg_return + (ohlc_dict[ticker]["return"].sum() * 100)  #
    # print(avg_return)  #


# Calculate Overall Stategy's KPI 
strategy_df = pd.DataFrame()
for ticker in ticker_list:
    strategy_df[ticker] = ohlc_dict[ticker]["return"]
    strategy_df[ticker].fillna(0, inplace=True)

strategy_df["return"] = strategy_df.mean(axis=1)

print(strategy_df)
print("")
print(ohlc_dict)

print("CAGR:", CAGR(strategy_df, candle_period='1day'))
# sharpe(strategy_df, 0.03)
# max_dd(strategy_df)


(1 + strategy_df["return"]).cumprod().plot()