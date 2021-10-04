import websocket 
import os 
import json 
import sqlite3
import datetime as dt
import requests 
import pandas as pd 


os.chdir("D:\\SynologyDrive\Programming\AlpacaTradingBot")

endpoint = "https://data.alpaca.markets/v1"
headers = json.loads(open("key.txt", 'r').read())
streams = ["T.AAPL", "T.TSLA", "T.GOOG", "T.AMZN", "Q.AAPL", "Q.TSLA", "Q.GOOG", "Q.AMZN"]

# Create Database - establish connection to database 
db1 = sqlite3.connect('D:/SynologyDrive/Programming/AlpacaTradingBot/streamingdata/trade_ticks.db')
db2 = sqlite3.connect('D:/SynologyDrive/Programming/AlpacaTradingBot/streamingdata/quotes_ticks.db')


def return_tickers(streams, tick_type="trades"):
    tickers = []
    if tick_type == "quotes":
        for symbol in streams:
            t_t,ticker = symbol.split(".")
            if t_t == "Q" and ticker not in tickers:
                tickers.append(ticker)
    elif tick_type == "trades":
        for symbol in streams:
            t_t,ticker = symbol.split(".")
            if t_t == "T" and ticker not in tickers:
                tickers.append(ticker)
    
    return tickers 


def create_tables(db, tickers, tick_type):
    # Move cursor to database - ready to make changes to database 
    c = db.cursor()
    if tick_type == "trades":
        for ticker in tickers:
            c.execute("CREATE TABLE IF NOT EXISTS t{} (timestamp datetime primary key, price real(15, 5), volume integer)".format(ticker))
    if tick_type == "quotes":
        for ticker in tickers:
            c.execute("CREATE TABLE IF NOT EXISTS q{} (timestamp datetime primary key, bid_price real(15, 5), ask_price real(15, 5), bid_volume integer, ask_volume integer)".format(ticker))
    try:
        db.commit()
    except: 
        db.rollback()

create_tables(db1, return_tickers(streams, "trades"), "trades")
create_tables(db2, return_tickers(streams, "quotes"), "quotes")


def insert_ticks(tick):
    if tick["stream"].split(".")[0] == "T":
        c = db1.cursor()
        for ms in range(100):
            try: 
                table = tick["stream"].split(".")[-1]
                values = [dt.datetime.fromtimestamp(int(tick["data"]["t"])/10**9)+dt.timedelta(milliseconds=ms), tick["data"]["p"], tick["data"]["s"]]
                query = "INSERT INTO t{}(timestamp, price, volume) VALUES(?,?,?)".format(table)
                c.execute(query, values)
                break
            except Exception as e:
                print(e)
        try:
            db1.commit()
        except:
            db1.rollback()

    if tick["stream"].split(".")[0] == "Q":
        c = db2.cursor()
        for ms in range(100):
            try: 
                table = tick["stream"].split(".")[-1]
                values = [dt.datetime.fromtimestamp(int(tick["data"]["t"])/10**9)+dt.timedelta(milliseconds=ms), tick["data"]["p"], tick["data"]["P"], tick["data"]["s"], tick["data"]["S"]]
                query = "INSERT INTO q{}(timestamp, bid_price, ask_price, bid_volume, ask_volume) VALUES(?, ?, ?, ?, ?)".format(table)
                c.execute(query, values)
                break
            except Exception as e:
                print(e)
        try:
            db2.commit()
        except:
            db2.rollback()


def on_open(ws):
    auth = {
        "action": "authenticate",
        "data": {"key_id": headers["APCA-API-KEY-ID"], "secret_key": headers["APCA-API-SECRET-KEY"]}
    }
    ws.send(json.dumps(auth))
    message = {
        "action": "listen",
        "data": {
            "streams": streams
        }
    }
    ws.send(json.dumps(message))


def on_message(ws, message):
    print(message)
    tick = json.loads(message)
    insert_ticks(tick)



ws = websocket.WebSocketApp("wss://data.alpaca.markets/stream", on_open=on_open, on_message=on_message)
ws.run_forever()