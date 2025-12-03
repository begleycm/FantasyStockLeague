from decimal import Decimal
from rest_framework.response import Response
from catalog.models import League, LeagueParticipant, Stock, UserLeagueStock
from api.apiUtils.utils import getOwnedStocks


def buy_stock(league_id, user, ticker, shares):
    """
    Utility function to buy a stock.
    Returns a tuple: (success: bool, response_data: dict, status_code: int)
    """
    try:
        # Get league and participant
        league = League.objects.get(league_id=league_id)
        participant = LeagueParticipant.objects.get(league=league, user=user)
        
        # Get stock
        stock = Stock.objects.get(ticker=ticker)
        
        # Validate shares
        shares_decimal = Decimal(str(shares))
        if shares_decimal <= 0:
            return False, {'error': 'Shares must be greater than 0'}, 400
        
        # Calculate cost
        cost = stock.current_price * shares_decimal
        
        # Check if user has enough balance
        if participant.current_balance < cost:
            return False, {'error': 'Insufficient balance'}, 400
        
        # Get or create UserLeagueStock entry
        user_stock, created = UserLeagueStock.objects.get_or_create(
            league_participant=participant,
            stock=stock,
            defaults={'shares': Decimal('0.00'), 'avg_price_per_share': stock.current_price}
        )
        
        # Calculate new average price per share (weighted average)
        if created:
            user_stock.avg_price_per_share = stock.current_price
        else:
            total_cost = (user_stock.avg_price_per_share * user_stock.shares) + cost
            total_shares = user_stock.shares + shares_decimal
            user_stock.avg_price_per_share = total_cost / total_shares
        
        # Update shares
        user_stock.shares += shares_decimal
        user_stock.save()
        
        participant.current_balance -= cost
        participant.save()
        
        return True, {
            'message': f'Successfully bought {shares} shares of {ticker}',
            'new_balance': float(participant.current_balance),
            'total_shares': float(user_stock.shares),
            'cost': float(cost)
        }, 200
        
    except League.DoesNotExist:
        return False, {'error': 'League not found'}, 404
    except LeagueParticipant.DoesNotExist:
        return False, {'error': 'You are not a participant in this league'}, 404
    except Stock.DoesNotExist:
        return False, {'error': 'Stock not found'}, 404
    except Exception as e:
        return False, {'error': f'Failed to buy stock: {str(e)}'}, 500


def sell_stock(league_id, user, ticker, shares):
    """
    Utility function to sell a stock.
    Returns a tuple: (success: bool, response_data: dict, status_code: int)
    """
    try:
        # Get league and participant
        league = League.objects.get(league_id=league_id)
        participant = LeagueParticipant.objects.get(league=league, user=user)
        
        # Get stock
        stock = Stock.objects.get(ticker=ticker)
        
        # Validate shares
        shares_decimal = Decimal(str(shares))
        if shares_decimal <= 0:
            return False, {'error': 'Shares must be greater than 0'}, 400
        
        # Get UserLeagueStock entry
        try:
            user_stock = UserLeagueStock.objects.get(
                league_participant=participant,
                stock=stock
            )
        except UserLeagueStock.DoesNotExist:
            return False, {'error': 'You do not own this stock'}, 404
        
        # Check if user has enough shares
        if user_stock.shares < shares_decimal:
            return False, {'error': f'Insufficient shares. You own {user_stock.shares} shares'}, 400
        
        # Calculate revenue
        revenue = stock.current_price * shares_decimal
        
        # Update shares and balance
        user_stock.shares -= shares_decimal
        remaining_shares = user_stock.shares
        if user_stock.shares <= 0:
            user_stock.delete()
            remaining_shares = Decimal('0.00')
        else:
            user_stock.save()
        
        participant.current_balance += revenue
        participant.save()
        
        return True, {
            'message': f'Successfully sold {shares} shares of {ticker}',
            'new_balance': float(participant.current_balance),
            'remaining_shares': float(remaining_shares),
            'revenue': float(revenue)
        }, 200
        
    except League.DoesNotExist:
        return False, {'error': 'League not found'}, 404
    except LeagueParticipant.DoesNotExist:
        return False, {'error': 'You are not a participant in this league'}, 404
    except Stock.DoesNotExist:
        return False, {'error': 'Stock not found'}, 404
    except Exception as e:
        return False, {'error': f'Failed to sell stock: {str(e)}'}, 500

