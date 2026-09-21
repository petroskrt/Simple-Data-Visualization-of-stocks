import pandas as pd
import requests
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta

API_KEY = "Your_API_Key"

tickers = [
    'JPM',
    'BAC',
    'C',
    'WFC',
    'GS'
]

years = 10
cutoff = datetime.now() - timedelta(days=365 * years)

# dict. to hold one data frame per ticker
data_by_ticker = {}

for ticker in tickers:
    HTTP_request = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=compact&apikey={API_KEY}'
    r = requests.get(HTTP_request)
    data = r.json()
    
    if 'Time Series (Daily)' not in data:
        print(f"Skipping {ticker}, no data returned: {data}")
        continue
    
    df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df[df.index >= cutoff]
    
    # Close column of Alpha Vantage is called '4. close'
    data_by_ticker[ticker] = df['4. close'].rename(ticker)
    
    time.sleep(15)
    
# Combine all tickers' closing prices into one DataFrame, aligned by date
bank_data = pd.concat(data_by_ticker.values(), axis=1)
bank_data.index.name = 'Date'

print(bank_data.head())
bank_data = bank_data.apply(pd.to_numeric, errors='coerce')

plt.figure(figsize = (18, 22))

# Subplot structure: 3 arguments -> Number of Rows, Number of Columns, Which subplot is currently selected

# boxplot
plt.subplot(2, 2, 1)
 
plt.boxplot(bank_data.transpose())

plt.title('Boxplot of Bank Stock Prices (5 month Lookback)')
plt.ylabel('Bank', fontsize = 20)
plt.xlabel('Stock Prices')

ticks = range(1, len(bank_data.columns)+1)
labels = list(bank_data.columns)
plt.xticks(ticks, labels)

# Scatterplot
plt.subplot(2, 2, 2)

dates = bank_data.index.to_series()
dates = [pd.to_datetime(d) for d in dates]

WFC_stock_prices = bank_data['WFC']

plt.scatter(dates, WFC_stock_prices)

plt.title("Wells Fargo Stock Price (5M Lookback)")
plt.ylabel("Stock Price")
plt.xlabel("Date")

plt.subplot(2, 2, 3)

dates = bank_data.index.to_series()
dates = [pd.to_datetime(d) for d in dates]

BAC_stock_prices = bank_data['BAC']

plt.scatter(dates, BAC_stock_prices)

plt.title("Bank Of America Stock Price (5M Lookback)")
plt.ylabel("Stock Price")
plt.xlabel("Date")

# Histogram
plt.subplot(2, 2, 4)

plt.hist(bank_data.transpose(), bins = 50)

plt.legend(bank_data.columns, fontsize=20)

plt.title("A Histogram of Daily Closing Stock Prices for the 5 Largest Banks in the US")
plt.ylabel("Observations")
plt.xlabel("Stock Prices")

# Save the visualization
plt.savefig('bank_data.png')

# it fixes many common formattiing issues
plt.tight_layout()
