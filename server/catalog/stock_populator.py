# Write code here to populate a stock model

from django.forms import ValidationError
from catalog.models import LeagueParticipant, Stock, League, UserLeagueStock
from catalog.views import get_daily_closing_price
from catalog.stock_utils import get_current_stock_price

def create_new_stock(ticker: str, name: str, start_date: str):
    """Creates a new stock in the database.
    Ticker in the format of a stock ticker, name as whatever the stock's full name is.
    Start date is ignored - we use yesterday's closing price as start_price."""
    from catalog.stock_utils import get_stock_prices
    
    # Set the stock's ticker and name
    stock = Stock(ticker=ticker, name=name)
    
    # Get both yesterday's closing price and current price in a single API call
    yesterday_close, current_price = get_stock_prices(stock.ticker)
    
    # Set start_price to yesterday's closing price
    stock.start_price = yesterday_close
    stock.current_price = current_price
    
    # Save to the database using django orm
    stock.save()
    return stock


def update_stock_prices(stock_list):
    """Update both start_price (yesterday's closing) and current_price for all stocks.
    Uses a single API call per stock to get both values."""
    from catalog.stock_utils import get_stock_prices
    
    for stock in stock_list:
        try:
            # Get both yesterday's closing price and current price in a single API call
            yesterday_close, current_price = get_stock_prices(stock.ticker)
            
            # Update both prices
            stock.start_price = yesterday_close
            stock.current_price = current_price
            stock.save()
        except RuntimeError as e:
            # If API error (like rate limit), skip this stock and continue
            # Don't crash the whole update process
            if "API credits" in str(e) or "rate limit" in str(e).lower():
                # Skip this stock if we're out of API credits
                continue
            # For other errors, also skip but don't spam errors
            pass
        except Exception as e:
            # Log and continue so a single failing symbol or missing API key
            # doesn't abort the entire update process.
            import traceback
            traceback.print_exc()

    return stock_list
    