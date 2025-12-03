# Script to update day_start_price for all existing stocks

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fantasyStockLeauge.settings')
django.setup()

from catalog.models import Stock
from catalog.views import get_daily_closing_price
from catalog.stock_utils import get_current_stock_price
from datetime import date, timedelta

def update_all_day_start_prices():
    """Update day_start_price for all stocks in the database."""
    stocks = Stock.objects.all()
    today = date.today()
    
    print(f"Updating day_start_price for {stocks.count()} stocks...")
    
    updated_count = 0
    error_count = 0
    
    for stock in stocks:
        try:
            # Check if day_start_price needs updating (is None or date is old)
            if stock.day_start_price is None or (stock.day_start_date and stock.day_start_date < today):
                # Try to get yesterday's closing price
                closing_price = None
                for delta in range(1, 8):
                    try_date = (today - timedelta(days=delta)).strftime('%Y-%m-%d')
                    try:
                        closing_price = get_daily_closing_price(stock.ticker, try_date)
                        if closing_price is not None:
                            stock.day_start_price = closing_price
                            stock.day_start_date = today
                            stock.save()
                            print(f"Updated {stock.ticker}: day_start_price = ${closing_price:.2f} (from {try_date})")
                            updated_count += 1
                            break
                    except Exception:
                        continue
                
                # If we couldn't get closing price, use current price as fallback
                if stock.day_start_price is None or stock.day_start_date != today:
                    try:
                        current_price = get_current_stock_price(stock.ticker)
                        if current_price is not None:
                            stock.day_start_price = current_price
                            stock.day_start_date = today
                            stock.save()
                            print(f"Updated {stock.ticker}: day_start_price = ${current_price:.2f} (using current price)")
                            updated_count += 1
                    except Exception as e:
                        # Use existing current_price from database as fallback
                        if stock.current_price:
                            stock.day_start_price = stock.current_price
                            stock.day_start_date = today
                            stock.save()
                            print(f"Updated {stock.ticker}: day_start_price = ${stock.current_price:.2f} (using cached current price)")
                            updated_count += 1
                        else:
                            print(f"Error updating {stock.ticker}: {e}")
                            error_count += 1
            else:
                print(f"Skipped {stock.ticker}: day_start_price already set for today")
        except Exception as e:
            print(f"Error processing {stock.ticker}: {e}")
            error_count += 1
    
    print(f"\nSummary:")
    print(f"Updated: {updated_count}")
    print(f"Errors: {error_count}")

if __name__ == "__main__":
    update_all_day_start_prices()

