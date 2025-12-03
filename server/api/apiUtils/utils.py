from datetime import date

from django.db import models
from catalog.models import League, Stock, UserLeagueStock, LeagueParticipant

def getOwnedStocks(league_id, user):
    current_league = League.objects.get(league_id=league_id)
    return UserLeagueStock.objects.filter(league_participant__user=user,league_participant__league=current_league)

def getTotalStockValue(league_id, user):
    from decimal import Decimal
    owned_stocks = getOwnedStocks(league_id, user)
    total = Decimal('0.00')
    for stock in owned_stocks:
        total += Decimal(str(stock.shares)) * Decimal(str(stock.stock.current_price))
    return float(total)

def getUserStockProfits(league_id, user):
    """Get total profit for each stock owned by the user"""
    owned_stocks = getOwnedStocks(league_id, user)
    stocks = []

    for stock in owned_stocks:
        if stock.avg_price_per_share == 0:
            profit = 0
        else:
            profit = (stock.stock.current_price - stock.avg_price_per_share) * stock.shares
        data = {
            "ticker": stock.stock.ticker,
            "profit": float(profit),
        }
        stocks.append(data)

    return stocks