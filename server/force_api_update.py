# Force an API update to test last_api_call_time

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fantasyStockLeauge.settings')
django.setup()

from catalog.models import Stock
from catalog.stock_utils import get_current_stock_price
from django.utils import timezone

print("=" * 60)
print("FORCING API UPDATE TO TEST last_api_call_time")
print("=" * 60)

# Check current state
stocks = Stock.objects.all()
print(f"\nTotal stocks in database: {stocks.count()}")

if stocks.count() == 0:
    print("\nNo stocks found! Please run populate_stocks.py first.")
    exit(1)

print("\nCurrent last_api_call_time values:")
for stock in stocks[:5]:
    print(f"  {stock.ticker}: {stock.last_api_call_time}")

# Force update by manually calling the API for one stock
print("\n" + "-" * 60)
print("Forcing API call for first stock...")
first_stock = stocks.first()
print(f"Stock: {first_stock.ticker}")

try:
    # This will make an API call
    price = get_current_stock_price(first_stock.ticker)
    print(f"Got price: ${price}")
    
    # Update the stock's current_price and last_api_call_time
    first_stock.current_price = price
    first_stock.last_api_call_time = timezone.now()
    first_stock.save()
    
    print("\nAfter API call:")
    updated_stock = Stock.objects.get(ticker=first_stock.ticker)
    print(f"  {updated_stock.ticker}: last_api_call_time = {updated_stock.last_api_call_time}, current_price = ${updated_stock.current_price}")
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

