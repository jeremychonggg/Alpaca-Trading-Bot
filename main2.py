# Import Modules
import yfinance as yf
import datetime as dt
import schedule
import time 
from copy import deepcopy
import numpy as np
import websocket
import alpaca_trade_api as tradeapi

# Import Files 
from get_stock_data import *  # get_historical_data(), get_real_time_data()
from indicators import *  # get_general_trend(), bollinger_band(), rsi(), MACD(), stochastic()
from strategies import *  # entry_strategy(), exit_strategy()
from order import *  # market_order(), limit_order(), stop_order(), stop_limit_order(), trail_stop_order(), 
                     # bracket_order(), order_list(), order_cancel(), order_replace()


headers = json.loads(open("key.txt",'r').read())
api = tradeapi.REST(headers["APCA-API-KEY-ID"], headers["APCA-API-SECRET-KEY"], base_url='https://paper-api.alpaca.markets')


def prepare_ticker_list():
    tickers = ["FB", "CSCO", "AMZN", "NVDA", "PLTR"]
    
    return tickers 

def backtesting(ticker_list, dataframe):
    # 1. Initiate Variables
    ohlc_dict = deepcopy(dataframe)
    stoch_signal = {}
    tickers_signal = {}
    tickers_ret = {}
    trade_count = {}
    long_data = {}
    short_data = {}
    hwm = {}

    # 2. Run Indicators - Store in DataFrame
    stochastic(ohlc_dict)
    MACD(ohlc_dict)

    # 3. Initialize each ticker into each variables  
    for ticker in tickers.split(","):
        print("Calculating MACD & Stochastics for ",ticker)
        ohlc_dict[ticker].dropna(inplace=True)
        stoch_signal[ticker] = ""
        trade_count[ticker] = 0
        tickers_signal[ticker] = ""
        hwm[ticker] = 0
        tickers_ret[ticker] = [0]
        long_data[ticker] = {}
        short_data[ticker] = {}

    # 4. Calculate Daily Returns 
    for ticker in tickers.split(","):
        print("Calculating daily returns for ",ticker)
        for i in range(1,len(ohlc_dict[ticker])-1):
            # Categorise Stochastic Result 
            if ohlc_dict[ticker]["%K"][i] < 20:
                stoch_signal[ticker] = "oversold"
            elif ohlc_dict[ticker]["%K"][i] > 80:
                stoch_signal[ticker] = "overbought"
            
            # Check if triggered 'Open' Position 
            if tickers_signal[ticker] == "":
                tickers_ret[ticker].append(0)
                if ohlc_dict[ticker]["macd"][i]> ohlc_dict[ticker]["signal"][i] and \
                ohlc_dict[ticker]["macd"][i-1]< ohlc_dict[ticker]["signal"][i-1] and \
                stoch_signal[ticker]=="oversold":
                    tickers_signal[ticker] = "Buy"
                    trade_count[ticker]+=1
                    long_data[ticker][trade_count[ticker]] = [ohlc_dict[ticker]["open"][i+1]]
                    hwm[ticker] = ohlc_dict[ticker]["open"][i+1]
                elif ohlc_dict[ticker]["macd"][i]< ohlc_dict[ticker]["signal"][i] and \
                ohlc_dict[ticker]["macd"][i-1]> ohlc_dict[ticker]["signal"][i-1] and \
                stoch_signal[ticker]=="overbought":
                    tickers_signal[ticker] = "Sell"
                    trade_count[ticker]+=1
                    short_data[ticker][trade_count[ticker]] = [ohlc_dict[ticker]["open"][i+1]]
                    hwm[ticker] = ohlc_dict[ticker]["open"][i+1]

            # Check if triggered 'Close Long' Position             
            elif tickers_signal[ticker] == "Buy":
                if ohlc_dict[ticker]["low"][i]<0.985*hwm[ticker]:
                    tickers_signal[ticker] = ""
                    long_data[ticker][trade_count[ticker]].append(0.985*hwm[ticker])
                    trade_count[ticker]+=1
                    tickers_ret[ticker].append((0.985*hwm[ticker]/ohlc_dict[ticker]["close"][i-1])-1)
                else:
                    hwm[ticker] = ohlc_dict[ticker]["high"][i]
                    tickers_ret[ticker].append((ohlc_dict[ticker]["close"][i]/ohlc_dict[ticker]["close"][i-1])-1)

            # Check if triggered 'Close Short' Position     
            elif tickers_signal[ticker] == "Sell":
                if ohlc_dict[ticker]["high"][i]>1.015*hwm[ticker]:
                    tickers_signal[ticker] = ""
                    short_data[ticker][trade_count[ticker]].append(1.015*hwm[ticker])
                    trade_count[ticker]+=1
                    tickers_ret[ticker].append((ohlc_dict[ticker]["close"][i-1]/1.015*hwm[ticker])-1)
                else:
                    hwm[ticker] = ohlc_dict[ticker]["low"][i]
                    tickers_ret[ticker].append((ohlc_dict[ticker]["close"][i-1]/ohlc_dict[ticker]["close"][i])-1)
                                
        # Force close position that didn't triggered  
        if trade_count[ticker]%2 != 0:
            for trade in long_data[ticker]:
                if len(long_data[ticker][trade]) == 1:
                    long_data[ticker][trade].append(ohlc_dict[ticker]["close"][i])
            for trade in short_data[ticker]:
                if len(short_data[ticker][trade]) == 1:
                    short_data[ticker][trade].append(ohlc_dict[ticker]["close"][i])

        
        tickers_ret[ticker].append(0) #since we are removing the last row
        ohlc_dict[ticker]["ret"] = np.array(tickers_ret[ticker])

    # calculating overall strategy's KPIs
    long_df = {}
    short_df = {}
    return_df = {}

    overall_return = 0
    for ticker in tickers.split(","):
        try:
            long_df[ticker] = pd.DataFrame(long_data[ticker]).T
            long_df[ticker].columns = ["long_entry_pr","long_exit_pr"]
            long_df[ticker]["return"] = long_df[ticker]["long_exit_pr"]/long_df[ticker]["long_entry_pr"]
        except:
            print("no long trades for ", ticker)
        try:
            short_df[ticker] = pd.DataFrame(short_data[ticker]).T
            short_df[ticker].columns = ["short_entry_pr","short_exit_pr"]
            short_df[ticker]["return"] = short_df[ticker]["short_entry_pr"]/short_df[ticker]["short_exit_pr"]
        except:
            print("no short trades for ", ticker)
        
        if len(long_df[ticker]) == 0:
            return_df[ticker] = short_df[ticker]["return"]
        elif len(short_df[ticker]) == 0:
            return_df[ticker] = long_df[ticker]["return"]
        else:
            return_df[ticker] = long_df[ticker]["return"].append(short_df[ticker]["return"]).sort_index()   
        print("total return {} = {}".format(ticker,return_df[ticker].cumprod().iloc[-1]- 1))
        overall_return+= (1/len(tickers.split(",")))*(return_df[ticker].cumprod().iloc[-1]- 1)

    print("Overall Return of Strategy = {}".format(overall_return))

def backtesting2(ticker_list, dataframe):
    # 1. Configuration 
    start_date = (dt.datetime.today() - dt.timedelta(14)).strftime('%Y-%m-%d')  # 14 Days ago 
    end_date = (dt.datetime.today() - dt.timedelta(1)).strftime('%Y-%m-%d')  # Previous date
    # 2. Prepare backtesting data 
    backtesting_dataframe = get_historical_data(tickers, start_date, end_date, timeframe="1Min")
    # 3. Initiate Variables
    stoch_signal = {}
    tickers_signal = {}
    tickers_ret = {}
    trade_count = {}
    long_data = {}
    short_data = {}
    hwm = {}
    # 4. Start Entry Strategy 
    entry_strategy(tickers, backtesting_dataframe)
    # 5. Initialize each ticker into each variables 



# Risk Per Trade 
risk_per_trade = 0.02  # 1% - 3% of capital

def main():
    # POSITION SIZING 
    ## 1. Capital (Net Liquidation) = shares + cash 
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
    print("##################################################")
    
    # 1.0 Prepare Ticker List
    print("--Preparing Today's Ticker List")
    ticker_list = prepare_ticker_list()
    print("--DONE Preparing Today's Ticker List")
    print("Ticker List:", ticker_list)
    print("==================================================")
    
    # 2.0 Filter Into "Long Position List" / "Short Position List"
    ## Prepare dataframe of tickers 
    print("--Preparing Stock's Historical Data")
    start_date = (dt.datetime.today() - dt.timedelta(3)).strftime('%Y-%m-%d')  # 14 Days ago 
    end_date = (dt.datetime.today() - dt.timedelta(2)).strftime('%Y-%m-%d')  # Previous date [change back to 1]
    dataframe = get_historical_data(ticker_list, start_date, end_date, limit=200)
    print("--DONE Preparing Stock's Historical Data")
    print(dataframe)
    print("==================================================")

    ## 2.1 Check Trend Direction (UpTrend: 20EMA > 40EMA  ||  DownTrend: 40EMA > 20EMA)
    print("--Checking Stock's Trend Direction")
    position_list = {}

    for ticker in ticker_list:
        # Initiate ticker into position_list
        position_list[ticker] = ''
        if get_general_trend(ticker, dataframe) == "long":
            ## 2.2 Put in "Long Position List" / "Short Position List" 
            #long_position_list.append(ticker)  # change to append into position_list
            position_list[ticker] = 'long'
        elif get_general_trend(ticker, dataframe) == "short":
            ## 2.2 Put in "Long Position List" / "Short Position List" 
            #short_position_list.append(ticker)  # change to append into position_list
            position_list[ticker] = 'short'

    print("--DONE Checking Stock's Trend Direction")
    print(position_list)
    print("==================================================")
    
    """
    # 3.0 Backtesting "Long Position List" / "Short Position List" (using last 5 days' historical data)
    ## 3.1 Prepare Backtesting DataFrame 
    backtesting_dataframe = get_historical_data(ticker_list, start_date, end_date, timeframe="1Min")
    ## 3.2 Backtesting 
    backtesting2(ticker_list, backtesting_dataframe)  # in future output which strategy to use
    ## 3.3 Output Percentage Gain (Return): 
    ### * "Long Position List" 
    ### * "Short Position List"

    # 4.0 Reorder "Position Lists" Percentage Gain (Return) by "Best Performing" to "Least Performing" 
    """

    # Loop every minute - THREADING 1 
    # 5. Check Position's Status (except today's stock)
    ### LOOP order_list() > order_cancel() 
    # 5.1 Check "Stop Lost" 
    # 5.2 Check "Take Profit" 

    # 6. If Triggered "Stop Lost" / "Take Profit"
    # 6.1 Close Position 
    opened_position_list = api.list_positions()
    for position in opened_position_list:
        ticker = position.symbol
        opened_stock_price = float(position.avg_entry_price)
        quantity_of_stock = float(position.qty)
        stop_loss_price = opened_stock_price * 0.9
        try:
            filled_quantity = api.get_position(ticker).qty
            if position.side == 'long':
                pass 
                #api.submit_order(ticker, float(filled_quantity), 'sell', 'trailing_stop', 'day', trail_percent=10) # trail_percent NEED TO CHANGE
            elif position.side == 'short':
                pass 
                #api.submit_order(ticker, float(filled_quantity), 'buy', 'trailing_stop', 'day', trail_percent=10) # trail_percent NEED TO CHANGE
        except Exception as e:
            print(ticker, e)

    
    

    # 7. Check right timing to enter position (from Position Lists)
    # Entry Strategy Test > Open Order 
    for ticker in position_list:
        opened_position_list = api.list_positions()

        existing_position = False 
        # Check if position exist 
        for position in opened_position_list:
            if len(opened_position_list) > 0:
                if position.symbol == ticker and position.qty != 0:
                    print("==>Existing position of {} stocks in {}..Skipping".format(position.qty, ticker))
                    existing_position = True 

        if existing_position == False:
            # Loop every minute - THREADING 2 
            # Get live market data 


            # Loop every minute - THREADING 3 
            # Enter Position 
            status = entry_strategy(ticker, position_list.get(ticker))  # entry_strategy(ticker, position)
        
            if status['can_buy'] == True:
                # Enter Long Position 
                if position_list.get(ticker) == 'long':
                    # Prepare Order 
                    stock_price = status['current_stock_price']  # Call Alpaca API 
                    risk_per_share = stock_price * 0.9 
                    quantity_of_stock = (risk_per_trade * current_available_equity) / risk_per_share 
                    trade_amount = stock_price * quantity_of_stock


                    # Open Order 
                    api.submit_order(ticker, quantity_of_stock, 'buy', 'market', 'day')

                    # Get Opened Position Data 
                    opened_stock_price = stock_price  # NEED TO UPDATE (get from Alpaca API)
                    traded_amount = opened_stock_price * quantity_of_stock  # NEED TO UPDATE (get from Alpaca API)
                    take_profit_price = traded_amount + (2 * (risk_per_trade * current_available_equity)) 
                    stop_loss_price = traded_amount - (risk_per_trade * current_available_equity) 
                    current_available_equity -= traded_amount  # NEED TO UPDATE (get from Alpaca API)
                    #position_opened_list[ticker] = {'opened_stock_price': opened_stock_price, 'take_profit_price': take_profit_price, 'stop_loss_price': stop_loss_price}
                    print("Position Opened: LONG [{}] ".format(ticker), "|  # Traded: {} ".format(round(quantity_of_stock, 2)), "|  Total Traded: $ {}".format(round(traded_amount, 2)), "|  Capital Left: $ {} \n".format(round(current_available_equity, 2)))
                
                # Enter Short Position     
                elif position_list.get(ticker) == 'short':
                    quantity = ''
                    # market_order(symbol, quantity, side="sell", tif="day")
                    # Update current_available_equity = 
                    print("Position Opened: SHORT [{}]".format(ticker))


main()

## Run main() every daily 30mins before market start 
# schedule.every().monday.at("21:00").do(main)
# schedule.every().tuesday.at("21:00").do(main)
# schedule.every().wednesday.at("21:00").do(main)
# schedule.every().thursday.at("21:00").do(main)
# schedule.every().friday.at("21:00").do(main)

# while True:
#     schedule.run_pending()
#     time.sleep(1)



