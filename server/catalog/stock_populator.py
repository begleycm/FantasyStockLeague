# Write code here to populate a stock model

from django.forms import ValidationError
from catalog.models import LeagueParticipant, Matchup, Stock, League, UserLeagueStock
from catalog.views import get_daily_closing_price, get_current_price

def create_new_stock(ticker: str, name: str, start_date: str):
    """Creates a new stock in the database.
    Ticker in the format of a stock ticker, name as whatever the stock's full name is.
    Start date in format: year-month-day ex: 2025-08-09."""
    
    # Set the stock's ticker and name
    stock = Stock(ticker=ticker, name=name)
    
    # Set the stock's data from the api
    stock.start_price = get_daily_closing_price(stock.ticker, start_date)
    stock.current_price = get_current_price(stock.ticker)
    
    # Save to the database using django orm
    stock.save()
    return stock


def update_stock_prices(stock_list):
    """Call current price on all stocks and return the updated list."""
    for stock in stock_list:
        stock.current_price = get_current_price(stock.ticker)
        stock.save()
        
    return stock_list
    