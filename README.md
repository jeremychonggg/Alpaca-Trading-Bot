[21:00] - 30 mins before market open.. 
1. Prepare Ticker List 
    * Top Gainer (from previous day) - 25 stocks
    * Most Active (Highest Volume) - 25 stocks 
    * QQQ (ETF List) - 100 stocks

2. Filter Into "Long Position List" / "Short Position List" 
    2.1 Check Trend (Last 14 days) 
    Indicator: 
    * 10EMA > 20EMA 
    2.2 Put in "Long Position List" / "Short Position List" 

3. Backtesting "Long Position List" / "Short Position List" (using last 5 days' historical data)
    3.1 Output Percentage Gain (Return): 
    * "Long Position List" 
    * "Short Position List"

4. Reorder "Position Lists" Percentage Gain (Return) by "Best Performing" to "Least Performing" 
    * "Long Position List" 
    * "Short Position List" 

[Repeat Step 1 - Step 4 daily @ 21:00]


[21:31] - Market opened.. 
5. Check Position's Status (except today's stock)
    5.1 Check "Stop Lost" 
    6.2 Check "Take Profit" 

6. If Triggered "Stop Lost" / "Take Profit"
    6.1 Close Position 

7. Check right timing to enter position (from Position Lists)
    7.1 Long Position - Indicator Test: 
    * Bollinger Band 
    * RSI
    * ..
    7.2 Short Position - Indicator Test: 
    * Bollinger Band 
    * RSI
    * ..

8. Open Position 
    8.1 Check if Capital Available 
    8.2 Set 'Quantity' To Enter 
    * "Long Position List" 
    * "Short Position List"
    8.3 Open Position 


[Loop Step 5 - Step 8 every minute]










[21:00] - 30 mins before market open.. 
1. Prepare Ticker List 
    * Top Gainer (from previous day) - 25 stocks
    * Most Active (Highest Volume) - 25 stocks 
    * QQQ (ETF List) - 100 stocks

2. Filter Into "Long Position List" / "Short Position List" 
    2.1 Check Trend (Last 14 days)
    2.2 Put in "Long Position List" / "Short Position List" 

3. Filter Into "Long Position Top List" / "Short Position Top List" 
    3.1 Indicator Test: 
    * MACD 
    * RSI
    3.2 If PASSED Indicator Test: 
    * Put in "Long Position Top List" / "Short Position Top List" 

4. Backtesting "Top Lists" (using last 5 days' historical data)
    4.1 Output Percentage Gain (Return): 
    * "Long Position Top List" 
    * "Short Position Top List"

5. Reorder "Top Lists" Percentage Gain (Return) by "Best Performing" to "Least Performing" 
    * "Long Position Top List" 
    * "Short Position Top List"

6. Open Position 
    6.1 Set 'Quantity' To Enter 
    * "Long Position Top List" 
    * "Short Position Top List"
    6.2 Open Position start from Highest Percentage Gain (Return)

[Repeat Step 1 - Step 6 daily @ 21:00]


[21:31] - Market opened.. 
7. Check Position's Status (except today's stock)
    7.1 Check "Stop Lost" 
    7.2 Check "Take Profit" 

8. If Triggered "Stop Lost" / "Take Profit"
    8.1 Close Position 

[Repeat Step 7 - Step 8 every minute]
