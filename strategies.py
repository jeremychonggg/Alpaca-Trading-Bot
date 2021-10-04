import json
import websocket


headers = json.loads(open("key.txt", 'r').read())
tickers = []
stock_price = None

def on_open(ws):
    auth = {
        "action": "auth", 
        "key": headers["APCA-API-KEY-ID"], 
        "secret": headers["APCA-API-SECRET-KEY"]
    }
    message = {
        "action": "subscribe",
        "quotes": tickers #['QQQ']
    }
    ws.send(json.dumps(auth))
    ws.send(json.dumps(message))

def on_message(ws, message):
    global stock_price
    stock_price = json.loads(message)[0]['bp']

    print(message)
    
def on_close(ws):
    print("Closed Connection")



def entry_strategy(ticker, position):
    # 1. Get real time data of 'ticker'
    tickers.append(ticker)
    socket = "wss://stream.data.alpaca.markets/v2/iex"
    ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_close=on_close)
    ws.run_forever()
    ws.keep_running = False
    print(stock_price)
    
    if position == 'long':  
        # 1. Call bollinger_band()
        # 2. call rsi()
        current_stock_price = 125  # NEED TO UPDATE (get from Alpaca API)
        # if bollinger_band() & rsi() pass:
        print("Entry Strategy Test: [{}] PASSED 'LONG' ".format(ticker))
        status = {'can_buy': True, 'current_stock_price': current_stock_price}
        return status  
    elif position == 'short':
        # call bollinger_band()
        # call rsi()
        current_stock_price = 125  # NEED TO UPDATE (get from Alpaca API)
        print("Entry Strategy Test: [{}] PASSED 'SHORT' ".format(ticker)) 
        status = {'can_buy': True, 'current_stock_price': current_stock_price}
        return status  

# entry_strategy('QQQ', 'long')


def entry_strategy2(position_list):
    # Run Indicators - Store in DataFrame
    for ticker in position_list:
        if position_list[ticker] == 'long': 
            """
            if (bollinger_band(ticker) < 20) and (rsi(ticker) < 20):
                return True
            """
            print("[{}] PASSED 'LONG' Entry Strategy Test".format(ticker))
        elif position_list[ticker] == 'short': 
            """
            if (bollinger_band(ticker) > 20) and (rsi(ticker) > 20):
                return True
            """
            print("[{}] PASSED 'SHORT' Entry Strategy Test".format(ticker)) 


def exit_strategy():
    pass 


"""
class testingThread(threading.Thread):
    def __init__(self,threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
    def run(self):
        print str(self.threadID) + " Starting thread"
        self.ws = websocket.WebSocketApp("ws://localhost/ws", on_error = self.on_error, on_close = self.on_close, on_message=self.on_message,on_open=self.on_open)
        self.ws.keep_running = True 
        self.wst = threading.Thread(target=self.ws.run_forever)
        self.wst.daemon = True
        self.wst.start()
        running = True;
        testNr = 0;
        time.sleep(0.1)
        while running:          
            testNr = testNr+1;
            time.sleep(1.0)
            self.ws.send(str(self.threadID)+" Test: "+str(testNr)+")
        self.ws.keep_running = False;
        print str(self.threadID) + " Exiting thread"
"""