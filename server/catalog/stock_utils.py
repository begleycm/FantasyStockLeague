import os
from dotenv import load_dotenv
from datetime import date, timedelta, datetime
import requests

# Grab api key - use Twelve Data API key
load_dotenv()
api_key = os.getenv("STOCK_API_KEY", "f99e95eaa5da47d0b01313a81c685c9a") # NEED TO REMOVE HARD CODED  KEY

def _require_api_key():
    if not api_key:
        raise RuntimeError("STOCK_API_KEY is not set in environment; cannot fetch stock prices")


def get_stock_closing_price(ticker: str, date: str):
    """Returns the closing performance of a stock as a float. Start date must be in the format
    'year-month-day' with leading 0s as needed. ex: '2025-06-23'"""
    _require_api_key()
    
    # Twelve Data API endpoint for time series - get last 30 days and find the date
    url = f'https://api.twelvedata.com/time_series?symbol={ticker}&interval=1day&outputsize=30&apikey={api_key}'
    print(f"[API CALL] Fetching closing price for {ticker} on {date} using API key: {api_key[:10]}...")
    
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Network error fetching closing price for {ticker}: {e}")
    
    # Check for API errors
    if 'status' in data and data['status'] == 'error':
        error_msg = data.get('message', 'Unknown error')
        raise RuntimeError(f"Twelve Data API error: {error_msg}")
    
    # Check if we have data - Twelve Data returns 'values' array
    if 'values' not in data or len(data['values']) == 0:
        # Try to get the most recent available date before the requested date
        # Go back up to 7 days to find a trading day
        for delta in range(1, 8):
            try_date = (datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=delta)).strftime('%Y-%m-%d')
            try:
                url_fallback = f'https://api.twelvedata.com/time_series?symbol={ticker}&interval=1day&outputsize=30&apikey={api_key}'
                r_fallback = requests.get(url_fallback, timeout=10)
                r_fallback.raise_for_status()
                data_fallback = r_fallback.json()
                
                if 'status' in data_fallback and data_fallback['status'] == 'error':
                    continue
                    
                if 'values' in data_fallback and len(data_fallback['values']) > 0:
                    # Find the date in the values
                    for value in data_fallback['values']:
                        value_datetime = value.get('datetime', '')
                        if value_datetime.startswith(try_date):
                            return float(value['close'])
                    # If date not found, return most recent
                    return float(data_fallback['values'][0]['close'])
            except Exception:
                continue
        raise RuntimeError(f"Could not retrieve closing price for {ticker} on {date}. No data available.")
    
    # Find the specific date in the values array
    for value in data['values']:
        value_datetime = value.get('datetime', '')
        if value_datetime.startswith(date):
            return float(value['close'])
    
    # If exact date not found, try to find most recent date before requested date
    for value in data['values']:
        value_datetime = value.get('datetime', '')
        value_date = value_datetime.split()[0] if ' ' in value_datetime else value_datetime
        if value_date and value_date <= date:
            return float(value['close'])
    
    # Fallback to most recent value
    if len(data['values']) > 0:
        return float(data['values'][0]['close'])
    
    raise RuntimeError(f"Could not retrieve closing price for {ticker} on {date}. Response: {data}")


def get_stock_prices(ticker: str):
    """Returns both yesterday's closing price and current price in a single API call.
    Returns a tuple: (yesterday_closing_price, current_price)
    Uses time_series endpoint to get both values efficiently."""
    _require_api_key()
    
    # Single API call to get time series data (last 2 days)
    # This gives us yesterday's closing price and today's data if available
    url = f'https://api.twelvedata.com/time_series?symbol={ticker}&interval=1day&outputsize=2&apikey={api_key}'
    print(f"[API CALL] Fetching prices for {ticker} using API key: {api_key[:10]}...")
    
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Network error fetching prices for {ticker}: {e}")
    
    # Check for API errors
    if 'status' in data and data['status'] == 'error':
        error_msg = data.get('message', 'Unknown error')
        raise RuntimeError(f"Twelve Data API error: {error_msg}")
    
    # Get current price from price endpoint (real-time)
    try:
        price_url = f'https://api.twelvedata.com/price?symbol={ticker}&apikey={api_key}'
        price_r = requests.get(price_url, timeout=10)
        price_r.raise_for_status()
        price_data = price_r.json()
        
        if 'status' not in price_data or price_data['status'] != 'error':
            if 'price' in price_data:
                current_price = float(price_data['price'])
            else:
                current_price = None
        else:
            current_price = None
    except Exception:
        current_price = None
    
    # Parse time series data
    if 'values' not in data or len(data['values']) == 0:
        raise RuntimeError(f"No time series data available for {ticker}")
    
    values = data['values']
    
    # Get yesterday's closing price (index 1, or index 0 if only one day available)
    if len(values) >= 2:
        # Index 0 = most recent (today if market closed, yesterday if market open)
        # Index 1 = previous day (yesterday)
        yesterday_close = float(values[1]['close'])
    else:
        # Only one day available, use it as yesterday
        yesterday_close = float(values[0]['close'])
    
    # If we didn't get current price from price endpoint, use most recent close from time series
    if current_price is None:
        current_price = float(values[0]['close'])
    
    return (yesterday_close, current_price)


def get_current_stock_price(ticker: str):
    """Returns the current price of a stock as a float.
    Uses get_stock_prices internally for efficiency."""
    _, current_price = get_stock_prices(ticker)
    return current_price


def get_profit_float(ticker: str, start_date: str):
    """Returns the profit of a stock as a float from a certain date to today."""
    _require_api_key()
    
    # Get current price
    current_price = get_current_stock_price(ticker)
    
    # Get start date price
    start_price = get_stock_closing_price(ticker, start_date)
    
    total_profit = current_price - start_price
    return total_profit
