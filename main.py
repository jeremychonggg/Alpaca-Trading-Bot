# Import Modules
import json
import pandas as pd
import requests
from numpy import short
from strategies import exit_strategy
import alpaca_trade_api as tradeapi
import time 
import datetime as dt

# Import Files 
from prepare_ticker_list import prepare_ticker_list
from get_stock_data import get_historical_data
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
        # print(dataframe[ticker])
        
        # Get Ticker Info 
        try:
            last_close = float(dataframe[ticker]['close'].iloc[-1]) 
            long_entry_price = float(dataframe[ticker]['BB_E_LB'].iloc[-1]) 
            short_entry_price = float(dataframe[ticker]['BB_E_UB'].iloc[-1]) 
            rsi_value = float(dataframe[ticker]['rsi'].iloc[-1]) 
            long_entry_temp_stop_loss_price = float(dataframe[ticker]['BB_SL_LB'].iloc[-1]) 
            short_entry_temp_stop_loss_price = float(dataframe[ticker]['BB_SL_UB'].iloc[-1]) 
        except:
            print('---- Ticker [{}] Data not found'.format(ticker))
            pass 

        # Get Account Info 
        account_info = api.get_account()
        current_available_equity = round(float(account_info.equity), 2)
        current_available_cash = round(float(account_info.cash), 2)        
        
        # Set Risk Per Trade
        percentage_risk_per_trade = 0.03

        # Long Entry Strategy 
        if (last_close <= long_entry_price) and (rsi_value <= 40):
            # Prepare Order 
            risk_per_share = last_close - long_entry_temp_stop_loss_price
            quantity = (percentage_risk_per_trade * current_available_equity) / risk_per_share
            amount_to_open = last_close * quantity

            # Calculate if enough money to open position
            if (current_available_cash >= amount_to_open):
                try:
                    api.submit_order(ticker, quantity, 'buy', 'limit', 'day', limit_price=long_entry_price)
                    print("-----------------------------------------------")
                    print(">>>>>>>>>>| OPEN LIMIT ORDER | LONG |<<<<<<<<<<") 
                    print("TICKER:", ticker)
                    print("LONG ENTRY PRICE: $", long_entry_price)
                    print("LONG ENTRY QUANTITY:", quantity)
                    print("TOTAL ENTRY CASH AMOUNT: $", amount_to_open)
                    print("-----------------------------------------------")
                except:
                    try:
                        # fractional orders must be DAY 'market' orders
                        api.submit_order(ticker, quantity, 'buy', 'market', 'day')
                        print("-----------------------------------------------")
                        print(">>>>>>>>>>| OPEN MARKET ORDER | LONG |<<<<<<<<<<") 
                        print("TICKER:", ticker)
                        print("LONG ENTRY PRICE: $", long_entry_price)
                        print("LONG ENTRY QUANTITY:", quantity)
                        print("TOTAL ENTRY CASH AMOUNT: $", amount_to_open)
                        print("-----------------------------------------------")
                    except:
                        pass 


        # Short Entry Strategy 
        elif (last_close >= short_entry_price) and (rsi_value >= 60):
            # Prepare Order 
            risk_per_share = short_entry_temp_stop_loss_price - last_close 
            quantity = (percentage_risk_per_trade * current_available_equity) / risk_per_share
            amount_to_open = last_close * quantity
            
            # Calculate if enough money to open position
            if (current_available_cash >= amount_to_open):
                try:
                    api.submit_order(ticker, quantity, 'sell', 'limit', 'day', limit_price=short_entry_price)  
                    print("------------------------------------------------")
                    print(">>>>>>>>>>| OPEN LIMIT ORDER | SHORT |<<<<<<<<<<")  
                    print("TICKER:", ticker)
                    print("SHORT ENTRY PRICE: $", short_entry_price)
                    print("SHORT ENTRY QUANTITY:", quantity)
                    print("TOTAL ENTRY CASH AMOUNT: $", amount_to_open)
                    print("------------------------------------------------")
                except:
                    try:
                        # fractional orders must be DAY 'market' orders
                        api.submit_order(ticker, quantity, 'sell', 'market', 'day')  
                        print("------------------------------------------------")
                        print(">>>>>>>>>>| OPEN MARKET ORDER | SHORT |<<<<<<<<<<")  
                        print("TICKER:", ticker)
                        print("SHORT ENTRY PRICE: $", short_entry_price)
                        print("SHORT ENTRY QUANTITY:", quantity)
                        print("TOTAL ENTRY CASH AMOUNT: $", amount_to_open)
                        print("------------------------------------------------")
                    except:
                        pass 


def main():
    # POSITION SIZING 
    ## 1.0 Get Account Info
    account_info = api.get_account()
    current_available_equity = round(float(account_info.equity), 2)
    current_available_cash = round(float(account_info.cash), 2)
    day_trade_count = account_info.daytrade_count
    pattern_day_trader = account_info.pattern_day_trader
    trading_blocked = account_info.trading_blocked
    print("##################################################") 
    print("ITERATION START \t     {} ".format(time.strftime("%Y-%m-%d | %H:%M:%S")))
    print("==================================================")
    print("CURRENT AVAILABLE EQUITY\t: $", current_available_equity)
    print("CURRENT AVAILABLE CASH\t\t: $", current_available_cash)
    print("DAY TRADE COUNT\t\t\t:", day_trade_count)
    print("PATTERN DAY TRADE\t\t:", pattern_day_trader)
    print("TRADING BLOCKED\t\t\t:", trading_blocked)
    print("==================================================")
    
    # 2.0 Prepare Today's Pre-Ticker List
    print("\n\n")
    print("-- Preparing Today's Pre-Ticker List")
    pre_ticker_list = prepare_ticker_list()
    print("-- DONE Preparing Today's Pre-Ticker List")
    print("--------------------------------------------------")
    print("PRE-TICKER LIST:", str(len(pre_ticker_list)) + "-Qty", "|", pre_ticker_list)
    print("==================================================")

    # 3.0 Get Opened Position Info 
    print("\n\n")
    print("-- Getting Opened Position List")
    opened_position_list = api.list_positions()
    opened_position_ticker_list = []
    for position in opened_position_list:
        opened_position_ticker_list.append(position.symbol)
    print("-- DONE Getting Opened Position List")
    print("--------------------------------------------------")
    print("OPENED POSITION LIST:", str(len(opened_position_ticker_list)) + "-Qty", "|", opened_position_ticker_list)
    print("==================================================")

    # 4.0 Remove ticker that has position opened
    print("\n\n")
    print("-- Filtering Pre-Ticker List Into Ticker List")
    ticker_list = remove_opened_position(pre_ticker_list, opened_position_ticker_list)
    print("-- DONE Filtering Pre-Ticker List Into Position List")
    print("--------------------------------------------------")
    print("TICKER LIST:", str(len(ticker_list)) + "-Qty", "|", ticker_list)
    print("==================================================")

    # 5.1 Create dataframe of the historical data of tickers from position_list 
    print("\n\n")
    print("-- Creating Dataframe of Historical Data (of Ticker List)")
    start_date = (dt.datetime.today() - dt.timedelta(100)).strftime('%Y-%m-%d')  # 50 Days ago
    dataframe = get_historical_data(ticker_list, start_date, limit=10000, timeframe='1Day')
    print("-- DONE Creating Dataframe of Historical Data (of Ticker List)")
    # print("--------------------------------------------------")
    # print("DATA FRAME:")
    # print(dataframe)
    print("==================================================")

    # 5.2 Create dataframe of the historical data of tickers from opened_position_list
    print("\n\n")
    print("-- Creating Dataframe of Historical Data (of Opened Position Ticker List)")
    opened_position_dataframe = get_historical_data(opened_position_ticker_list, start_date, limit=10000, timeframe='1Day')
    print("-- DONE Creating Dataframe of Historical Data (of Opened Position Ticker List)")
    # print("--------------------------------------------------")
    # print("DATA FRAME:")
    # print(opened_position_dataframe)
    print("==================================================")

    # 6.0 Classify Ticker List's tickers into 'up' or 'down' trend 
    print("\n\n")
    print("-- Classifying Ticker List's tickers into 'up' or 'down' trend )")
    print("--------------------------------------------------")
    general_trend(dataframe)
    # print("DATA FRAME:")
    # print(dataframe)
    print("==================================================")

    # 7.1 Call Exit Strategy Function [FRACTIONAL ORDER CAN ONLY OPEN WHEN MARKET IS OPEN]
    print("\n\n")
    print("-- Executing Exit Strategy")
    print("--------------------------------------------------")
    exit_strategy(opened_position_dataframe, opened_position_list)
    print("==================================================")

    # 7.2 Call Entry Strategy Function [FRACTIONAL ORDER CAN ONLY OPEN WHEN MARKET IS OPEN]
    print("\n\n")
    print("-- Executing Entry Strategy")
    print("--------------------------------------------------")
    entry_strategy(dataframe, ticker_list)
    print("##################################################") 


main()

