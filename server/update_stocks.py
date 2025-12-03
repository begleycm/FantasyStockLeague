# Update all stocks every 5 minutes

import os
import django

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fantasyStockLeauge.settings')
django.setup()

from catalog.models import Stock
from asyncio import sleep
from datetime import datetime, timedelta
from django.utils import timezone
from catalog.stock_populator import update_stock_prices


def update_stocks(force=False):
    """Grabs stocks from database and updates them.
    By default this function keeps the original behavior of updating only during market windows
    and at 5-minute intervals. If `force=True` it will always perform an update.
    
    Returns True if updated and False if not.
    """
    
    # Grab the stock's last updated time and see if it needs to be changed
    current_datetime = timezone.now()
    current_time = current_datetime.time()
    stocks = Stock.objects.all() # Grab all stocks from the database
    stock_list = list(stocks)

    # If caller requested a forced update, do it and return
    if force:
        update_stock_prices(stock_list)
        return True

    # Check if market is open (9:30 AM - 4:00 PM EST)
    market_open = current_time.hour == 9 and current_time.minute >= 30
    market_hours = current_time.hour >= 10 and current_time.hour < 16
    market_just_closed = current_time.hour == 16 and current_time.minute <= 5  # 4:00 PM - 4:05 PM
    
    if not (market_open or market_hours or market_just_closed):
        return False  # Market closed, don't update
    
    # Check if there are any stocks in the database
    if not stock_list:
        return False  # No stocks to update
        
    # Get the most recently updated stock
    most_recent = stocks.order_by('-last_updated').first()
    if most_recent is None:
        return False  # No stocks to update
    last_update_time = most_recent.last_updated
    
    # Calculate how long ago the last update was
    time_since_update = current_datetime - last_update_time
    current_interval = (current_time.minute // 5) * 5
    last_update_interval = (last_update_time.minute // 5) * 5
     # Special case: Market just closed (4:01 PM), do final update
    if market_just_closed and last_update_time.hour < 16:
        update_stock_prices(stock_list)
        return True
    
    # Check if we're in a new 5-minute interval
    if time_since_update >= timedelta(minutes=5) or current_time.hour != last_update_time.hour or current_interval != last_update_interval:
        update_stock_prices(stock_list)
        return True
    else:
        return False
