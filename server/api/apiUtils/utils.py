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

def getUserWeeklyStockProfits(league_id, user):
    owned_stocks = getOwnedStocks(league_id, user)
    stocks = []

    for stock in owned_stocks:
        weekly_profit = (stock.price_at_start_of_week - stock.stock.current_price) * stock.shares
        data = {
            "ticker": stock.stock.ticker,
            "weekly_profit": weekly_profit,
        }
        stocks.append(data)

    return stocks

def getCurrentOpponent(league_id, user):
    current_league = League.objects.get(league_id=league_id)
    today = date.today()
    week_number = (today - current_league.start_date).days // 7 + 1
    participant = LeagueParticipant.objects.get(league=current_league, user=user)

    # Now find matchup where this participant is either participant1 or participant2
    from catalog.models import Matchup
    matchup = Matchup.objects.filter(
        league=current_league,
        week_number=week_number
    ).filter(
        (models.Q(participant1=participant) | models.Q(participant2=participant))
    ).first()

    if matchup.participant1 == participant:
        opponent = matchup.participant2
    else:
        opponent = matchup.participant1

    return opponent