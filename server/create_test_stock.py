# Simple script to create one test stock

import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fantasyStockLeauge.settings')
django.setup()

from catalog.models import Stock
from catalog.stock_utils import get_current_stock_price, get_stock_closing_price
from datetime import date, timedelta

# Find a valid trading date
start_date = None
for delta in range(1, 8):
    candidate_date = date.today() - timedelta(days=delta)
    if candidate_date.weekday() < 5:  # Skip weekends
        start_date = candidate_date.strftime('%Y-%m-%d')
        break

if not start_date:
    start_date = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')

print(f"Creating test stock AAPL with start date: {start_date}")

try:
    # Test API first
    print("Testing API...")
    current_price = get_current_stock_price("AAPL")
    print(f"Current price: ${current_price}")
    
    closing_price = get_stock_closing_price("AAPL", start_date)
    print(f"Closing price on {start_date}: ${closing_price}")
    
    # Create stock
    if Stock.objects.filter(ticker="AAPL").exists():
        print("AAPL already exists, updating...")
        stock = Stock.objects.get(ticker="AAPL")
    else:
        print("Creating new stock...")
        stock = Stock(ticker="AAPL", name="Apple Inc.")
    
    stock.start_price = closing_price
    stock.current_price = current_price
    stock.save()
    
    print(f"Success! Stock created/updated:")
    print(f"  Ticker: {stock.ticker}")
    print(f"  Name: {stock.name}")
    print(f"  Start Price: ${stock.start_price}")
    print(f"  Current Price: ${stock.current_price}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

