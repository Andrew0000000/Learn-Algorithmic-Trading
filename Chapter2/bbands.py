import pandas as pd
import yfinance as yf
from pandas_datareader import data

start_date = '2019-01-01'
end_date = '2023-02-19'
# get index of tesla stock
stock = "TSLA"
stocks_data = yf.download(stock , start=start_date, end=end_date)


'''
The Bollinger Band (BBANDS) study created
 by John Bollinger plots upper and lower envelope bands around the
 price of the instrument. The width of the bands is based on the
 standard deviation of the closing prices from a moving average of
 price.
 Middle
 Band = n-period moving average

Upper
 Band = Middle Band + ( y * n-period standard deviation)

Lower Band = Middle Band - ( y *
 n-period standard deviation)

Where:

n = number of periods
y = factor to apply to the standard deviation value, (typical default for y = 2)
Detailed:

Calculate the moving average.
 The formula is:
d = ((P1-MA)^2 + (P2-MA)^2 + ... (Pn-MA)^2)/n

Pn is the price you pay for the nth interval
n is the number of periods you select
Subtract the moving average
 from each of the individual data points used in the moving average
 calculation. This gives you a list of deviations from the average.
 Square each deviation and add them all together. Divide this sum
 by the number of periods you selected.

Take the square root of d. This gives you the standard deviation.

delta = sqrt(d)

Compute the bands by using the following formulas:
Upper Band = MA + delta
Middle Band = MA
Lower Band = MA - delta

 '''



import statistics as stats
import math as math

time_period = 20 # history length for Simple Moving Average for middle band
stdev_factor = 2 # Standard Deviation Scaling factor for the upper and lower bands
history = [] # price history for computing simple moving average
sma_values = [] # moving average of prices for visualization purposes
upper_band = [] # upper band values
lower_band = [] # lower band values

for close_price in stocks_data.Close:
  history.append(close_price)
  if len(history) > time_period: # we only want to maintain at most 'time_period' number of price observations
    del (history[0])

  sma = stats.mean(history)
  sma_values.append(sma) # simple moving average or middle band
  variance = 0 # variance is the square of standard deviation
  for hist_price in history:
    variance = variance + ((hist_price - sma) ** 2)

  stdev = math.sqrt(variance / len(history)) # use square root to get standard deviation

  upper_band.append(sma + stdev_factor * stdev)
  lower_band.append(sma - stdev_factor * stdev)

stocks_data = stocks_data.assign(ClosePrice=pd.Series(stocks_data.Close, index=stocks_data.index))
stocks_data = stocks_data.assign(SMA=pd.Series(sma_values, index=stocks_data.index))
stocks_data = stocks_data.assign(UpperBand=pd.Series(upper_band, index=stocks_data.index))
stocks_data = stocks_data.assign(LowerBand=pd.Series(lower_band, index=stocks_data.index))
print(stocks_data)

close_price = stocks_data['ClosePrice']
SMA = stocks_data['SMA']
uband = stocks_data['UpperBand']
lband = stocks_data['LowerBand']

import matplotlib.pyplot as plt
fig = plt.figure()
ax1 = fig.add_subplot(111, ylabel=stock + ' price in $')
close_price.plot(ax=ax1, color='black', lw=2., legend=True)
SMA.plot(ax=ax1, color='b', lw=2., legend=True)
uband.plot(ax=ax1, color='g', lw=2., legend=True)
lband.plot(ax=ax1, color='r', lw=2., legend=True)
stocks_data_signal = pd.DataFrame(index=stocks_data.index)
stocks_data_signal['Price'] = stocks_data['Adj Close']
stocks_data_signal['UpperBand'] = stocks_data['UpperBand']
stocks_data_signal['LowerBand'] = stocks_data['LowerBand']
stocks_data_signal['SellSignal'] = stocks_data_signal['Price'] - stocks_data['UpperBand']
stocks_data_signal['BuySignal'] = stocks_data_signal['Price'] - stocks_data['LowerBand']
stocks_data_signal['Position'] = 0

# records the prices of the stocks bought and sold with the buy signal and sell signal respectively
bought = []
sold = []

# position means the number of stocks you own at a given time. BuySignal increments position by 1 and SellSignal decrements position by 1.
for i in range(20, len(stocks_data_signal)):
  if stocks_data_signal['SellSignal'][i] > 10 and stocks_data_signal['Position'][i - 1] == 1:
    stocks_data_signal['Position'][i] = 0
    sold.append(stocks_data_signal['Price'][i])
  elif stocks_data_signal['BuySignal'][i] < -10 and stocks_data_signal['Position'][i - 1] == 0:
    stocks_data_signal['Position'][i] = 1
    bought.append(stocks_data_signal['Price'][i])
  else:
    stocks_data_signal['Position'][i] = stocks_data_signal['Position'][i - 1]

# calculates the profit/loss of the strategy
profit = sum(sold) - sum(bought)
print(sum(bought))
print(sum(sold))
print("bought: ", bought)
print("sold: ", sold)
print(len(bought), len(sold))
print("Profit: ", profit)




print(stocks_data_signal)
plt.show()
