import os
from dotenv import load_dotenv
from datetime import date, timedelta
from datetime import datetime
from pytz import timezone
import requests

# Grab api key
load_dotenv()
api_key = os.getenv("STOCK_API_KEY")

def get_current_formatted_time():
    """Grabs formatted time to use with the alphavantage stock api.
    Gives yesterdays time since we don't have premium."""
    eastern = timezone('US/Eastern')
    
    # We don't have the premium version so we have to do one day behind
    current_time = datetime.now(eastern)
    yesterday = current_time - timedelta(days=1)
    
    # Round down to nearest 5 minutes
    minutes = yesterday.minute
    rounded_minutes = (minutes // 5) * 5  # Integer division to round down
    rounded_time = yesterday.replace(minute=rounded_minutes, second=0, microsecond=0)
    
    # Format to match API timestamp format
    return rounded_time.strftime('%Y-%m-%d %H:%M:%S')

def get_stock_closing_price(ticker: str, date: str):
    """Returns the closing performance of a stock as a float. Start date must be in the format
    'year-month-day' with leading 0s as needed. ex: '2025-06-23'"""
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + ticker + '&interval=5min&apikey=' + api_key
    # Replace "symbol=SYM" with whatever symbol you'd like to grab data from
    r = requests.get(url)
    data = r.json()

    # Grab the float stock price and return it
    return float(data['Time Series (Daily)'][date]['4. close'])


def get_current_stock_price(ticker: str):
    """Returns the current price of a stock as a float within a 5 minute period."""
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + ticker + '&interval=5min&apikey=' + api_key
    r = requests.get(url)
    data = r.json()
    
    time = get_current_formatted_time()
    
     # Try to get the exact time, if not available, get the most recent
    time_series = data['Time Series (5min)']
    
    if time in time_series:
        return float(time_series[time]['4. close'])
    else:
        # Get the most recent available timestamp
        latest_time = sorted(time_series.keys(), reverse=True)[0]
        return float(time_series[latest_time]['4. close'])


def get_profit_float(ticker: str, start_date: str):
    """Returns the profit of a stock as a float from a certain date to today."""
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + ticker + '&interval=5min&apikey=' + api_key
    r = requests.get(url)
    data = r.json()
    
    url_start = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + ticker + '&interval=5min&apikey=' + api_key
    r_start = requests.get(url_start)
    data_start = r_start.json()
    
    time = get_current_formatted_time()
    
    # Grab value from both the start date AND today
    current_price = data['Time Series (5min)'][time]['4. close']
    start_price = data_start['Time Series (Daily)'][start_date]['4. close']
    
    total_profit = float(current_price) - float(start_price)
    return total_profit
