# Import Modules 
import requests
from bs4 import BeautifulSoup


# Webscrap list of top gainer stocks 
day_gainers_stock = {}
def find_day_gainers_stock():
    url = "https://finance.yahoo.com/gainers?count=100&offset=0" 
    page = requests.get(url)
    page_content = page.content
    soup = BeautifulSoup(page_content,'html.parser')
    table = soup.find_all("table", {"class" : "W(100%)"})
    for t in table:
        rows = t.find_all("tr")
        for row in rows:
            day_gainers_stock[row.get_text(separator='|').split("|")[0]] = row.get_text(separator='|').split("|")[4]


# Webscrap list of top volume stocks 
most_active_stock = {}
def find_most_active_stock():
    url = "https://finance.yahoo.com/most-active?count=100&offset=0" 
    page = requests.get(url)
    page_content = page.content
    soup = BeautifulSoup(page_content,'html.parser')
    table = soup.find_all("table", {"class" : "W(100%)"})
    for t in table:
        rows = t.find_all("tr")
        for row in rows:
            most_active_stock[row.get_text(separator='|').split("|")[0]] = row.get_text(separator='|').split("|")[5]



# Get Alpaca API Credential
import json
endpoint = "https://data.alpaca.markets/v2"
headers = json.loads(open("key.txt", 'r').read())

def prepare_ticker_list():

    find_day_gainers_stock()
    find_most_active_stock()

    ticker_list = [] 
    # https://www.invesco.com/us/financial-products/etfs/holdings?audienceType=Investor&ticker=QQQ
    qqq_list = ['AAPL', 'MSFT', 'AMZN', 'GOOG', 'FB', 'GOOGL', 'NVDA', 'TSLA', 'PYPL', 'ADBE', 'CMCSA', 'NFLX', 'INTC', 'PEP', 'AVGO', 'COST', 'TXN', 'TMUS', 'QCOM', 'HON', 'INTU', 'MRNA', 'CHTR', 'SBUX', 'AMD', 'AMGN', 'AMAT', 'ISRG', 'BKNG', 'MELI', 'GILD', 'ADP', 'LRCX', 'MDLZ', 'MU', 'ZM', 'FISV', 'CSX', 'ADSK', 'REGN', 'ILMN', 'ASML', 'ATVI', 'NXPI', 'JD', 'ADI', 'DOCU', 'IDXX', 'CRWD', 'ALGN', 'KLAC', 'EBAY', 'VRTX', 'BIIB', 'MNST', 'WDAY', 'LULU', 'SNPS', 'DXCM', 'MRVL', 'KDP', 'TEAM', 'EXC', 'CDNS', 'AEP', 'KHC', 'MAR', 'MCHP', 'ROST', 'WBA', 'ORLY', 'PAYX', 'CTAS', 'EA', 'CTSH', 'BIDU', 'XLNX', 'MTCH', 'XEL', 'PDD', 'CPRT', 'OKTA', 'VRSK', 'FAST', 'ANSS', 'SWKS', 'SGEN', 'PCAR', 'PTON', 'NTES', 'CDW', 'SIRI', 'SPLK', 'VRSN', 'CERN', 'DLTR', 'CHKP', 'INCY', 'TCOM', 'FOXA', 'FOX']

    # # Prepare Day Gainer 
    # for ticker in day_gainers_stock.keys():
    #     ticker_list.append(ticker)

    # ticker_list.remove('Symbol')

    # Prepare Most Active 
    for ticker in most_active_stock.keys():
        ticker_list.append(ticker)

    ticker_list.remove('Symbol')

    # Add QQQ List 
    for ticker in qqq_list:
        ticker_list.append(ticker)

    # Clear Ticker that are not in ALPACA 
    for ticker in ticker_list:
        bar_url = endpoint + "/stocks/{}/bars".format(ticker)
        params = {"start":'2021-01-01', "limit": 3, "timeframe":'1Day'}

        data = {"bars": [], "next_page_token": '', "symbol": ticker}
        while True:
            r = requests.get(bar_url, headers=headers, params=params)
            r = r.json()
            try:
                if r["next_page_token"] == None:
                    data["bars"] += r["bars"]
                    break
                else:
                    params["page_token"] = r["next_page_token"]
                    data["bars"] += r["bars"]
                    data["next_page_token"] = r["next_page_token"]
            finally:
                ticker_list.remove(ticker)
                break

    return ticker_list


