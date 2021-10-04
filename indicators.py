import json
import tulipy as ti
import yfinance as yf
import datetime as dt
import pandas as pd 
from copy import deepcopy
import numpy as np


def general_trend(dataframe):

    for df in dataframe:
        dataframe[df]["20EMA"] = ti.ema(dataframe[df]['close'].dropna().to_numpy(), 20)
        dataframe[df]["40EMA"] = ti.ema(dataframe[df]['close'].dropna().to_numpy(), 40)

        for row in dataframe[df].index:
            if dataframe[df]['20EMA'][row] > dataframe[df]['40EMA'][row]:
                dataframe[df]['trend'] = 'up'
            elif dataframe[df]['20EMA'][row] < dataframe[df]['40EMA'][row]:
                dataframe[df]['trend'] = 'down'

        print("---- Prepared for [{}]".format(df))

def get_general_trend(ticker, dataframe):
    # Calculate EMAs 
    ema1 = ti.ema(dataframe[ticker]["close"].dropna().to_numpy(), 20)
    ema2 = ti.ema(dataframe[ticker]["close"].dropna().to_numpy(), 40)

    if ema1[-1] >  ema2[-1]:
        return "long"
    elif ema1[-1] < ema2[-1]:
        return "short"
      
def bollinger_band(df_dict, length, stdDev, name):
    # https://www.udemy.com/course/algorithmic-trading-on-alpacas-platform-deep-dive/learn/lecture/25514612#overview
    # https://www.udemy.com/course/algorithmic-trading-quantitative-analysis-using-python/learn/lecture/28016948#overview
    middle_band = 'BB_' + name + '_MB' 
    upper_band = 'BB_' + name + '_UB' 
    lower_band = 'BB_' + name + '_LB' 
    bollinger_band_width = 'BB_' + name + '_width'
    
    for df in df_dict:
        # print("CLOSE PRICE =>", df_dict[df]['close'])
        # print("CLOSE PRICE + ROLLING =>", df_dict[df]['close'].rolling(length))
        # print("CLOSE PRICE + ROLLING + MEAN =>", df_dict[df]['close'].rolling(length).mean())
        
        df_dict[df][middle_band] = df_dict[df]["close"].rolling(length).mean()  # Formula: 20SMA
        df_dict[df][upper_band] = df_dict[df][middle_band] + ( stdDev * df_dict[df]["close"].rolling(length).std(ddof=0) )  # Formula: 20SMA + (Standard Deviation x 2)
        df_dict[df][lower_band] = df_dict[df][middle_band] - ( stdDev * df_dict[df]["close"].rolling(length).std(ddof=0) )  # Formula: 20SMA - (Standard Deviation x 2)
        df_dict[df][bollinger_band_width] = df_dict[df][upper_band] - df_dict[df][lower_band]  # Formula: Upper Band - Lower Band 

def rsi(df_dict, period):
    for df in df_dict:
        df_dict[df]['change'] = df_dict[df]['close'] - df_dict[df]['close'].shift(1)
        df_dict[df]['gain'] = np.where(df_dict[df]['change'] >= 0, df_dict[df]['change'], 0)
        df_dict[df]['loss'] = np.where(df_dict[df]['change'] < 0, (-1 * df_dict[df]['change']), 0)
        df_dict[df]['avgGain'] = df_dict[df]['gain'].ewm(alpha=(1/period), min_periods=period).mean()  # .ewm is pandas' exponential weighted function
        df_dict[df]['avgLoss'] = df_dict[df]['loss'].ewm(alpha=(1/period), min_periods=period).mean()  # .ewm is pandas' exponential weighted function
        df_dict[df]['rs'] = df_dict[df]['avgGain'] / df_dict[df]['avgLoss']
        df_dict[df]['rsi'] = 100 - (100 / (1 +  df_dict[df]['rs']))
        df_dict[df].drop(['change', 'gain', 'loss', 'avgGain', 'avgLoss', 'rs'], axis=1, inplace=True)



############################
def MACD(df_dict, a=12 ,b=26, c=9):
    """function to calculate MACD
       typical values a(fast moving average) = 12; 
                      b(slow moving average) =26; 
                      c(signal line ma window) =9"""
    for df in df_dict:
        df_dict[df]["ma_fast"] = df_dict[df]["close"].ewm(span=a, min_periods=a).mean()
        df_dict[df]["ma_slow"] = df_dict[df]["close"].ewm(span=b, min_periods=b).mean()
        df_dict[df]["macd"] = df_dict[df]["ma_fast"] - df_dict[df]["ma_slow"]
        df_dict[df]["signal"] = df_dict[df]["macd"].ewm(span=c, min_periods=c).mean()
        df_dict[df].drop(["ma_fast","ma_slow"], axis=1, inplace=True)

############################
def stochastic(df_dict, lookback=14, k=3, d=3):
    """function to calculate Stochastic Oscillator
       lookback = lookback period
       k and d = moving average window for %K and %D"""
    for df in df_dict:
        df_dict[df]["HH"] = df_dict[df]["high"].rolling(lookback).max()
        df_dict[df]["LL"] = df_dict[df]["low"].rolling(lookback).min()
        df_dict[df]["%K"] = (100 * (df_dict[df]["close"] - df_dict[df]["LL"])/(df_dict[df]["HH"]-df_dict[df]["LL"])).rolling(k).mean()
        df_dict[df]["%D"] = df_dict[df]["%K"].rolling(d).mean()
        df_dict[df].drop(["HH","LL"], axis=1, inplace=True)
   

