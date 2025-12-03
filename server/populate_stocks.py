# Script to populate initial stocks in the database

import os
import django

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fantasyStockLeauge.settings')
django.setup()

from catalog.models import Stock
from catalog.stock_populator import create_new_stock
from datetime import date, timedelta

# List of 5 popular stocks to populate (reduced to minimize API usage)
POPULAR_STOCKS = [
    ("AAPL", "Apple Inc."),
    ("MSFT", "Microsoft Corporation"),
    ("GOOGL", "Alphabet Inc."),
    ("AMZN", "Amazon.com Inc."),
    ("TSLA", "Tesla Inc."),
]

def populate_stocks():
    """Populate the database with initial stocks if they don't exist."""
    # Try to find a valid trading date (go back up to 7 days to find a weekday)
    start_date = None
    for delta in range(1, 8):
        candidate_date = date.today() - timedelta(days=delta)
        # Skip weekends (Saturday=5, Sunday=6)
        if candidate_date.weekday() < 5:
            start_date = candidate_date.strftime('%Y-%m-%d')
            break
    
    if not start_date:
        # Fallback to 7 days ago if all are weekends
        start_date = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"Using start date: {start_date}")
    
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    for ticker, name in POPULAR_STOCKS:
        # Check if stock already exists
        if Stock.objects.filter(ticker=ticker).exists():
            print(f"Stock {ticker} already exists, skipping...")
            skipped_count += 1
            continue
        
        try:
            # Try to create the stock
            stock = create_new_stock(ticker, name, start_date)
            print(f"Successfully created stock: {ticker} - {name} (Start: ${stock.start_price}, Current: ${stock.current_price})")
            created_count += 1
        except Exception as e:
            import traceback
            print(f"Error creating stock {ticker}: {e}")
            print(f"  Traceback: {traceback.format_exc()}")
            error_count += 1
            continue
    
    print(f"\nSummary:")
    print(f"Created: {created_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Errors: {error_count}")

if __name__ == "__main__":
    populate_stocks()

