from decimal import Decimal
from catalog.models import League, LeagueParticipant, Stock, UserLeagueStock
from api.serializer import LeaguesSerializer
from api.apiUtils.utils import getOwnedStocks, getTotalStockValue


def get_user_leagues_data(user):
    """
    Get all leagues for a user, with special handling for superusers.
    
    Args:
        user: User object
    
    Returns:
        dict with is_superuser flag and leagues list
    """
    if user.is_superuser:
        all_leagues = League.objects.all()
        leagues = []
        for league in all_leagues:
            league_serializer = LeaguesSerializer(league)
            # Check if superuser is a participant in this league
            participant = LeagueParticipant.objects.filter(
                league=league,
                user=user
            ).first()
            
            if participant:
                # Superuser is a participant, show like normal user
                data = {
                    "league": league_serializer.data,
                    "leagueAdmin": participant.leagueAdmin,
                    "isParticipant": True
                }
            else:
                # Superuser is not a participant, show as view-only
                data = {
                    "league": league_serializer.data,
                    "leagueAdmin": False,
                    "isParticipant": False
                }
            leagues.append(data)
        
        return {
            "is_superuser": True,
            "leagues": leagues
        }
    else:
        current_leagues = LeagueParticipant.objects.filter(user=user).distinct()
        leagues = []
        for league_participant in current_leagues:
            league_serializer = LeaguesSerializer(league_participant.league)
            data = {
                "league": league_serializer.data,
                "leagueAdmin": league_participant.leagueAdmin,
                "isParticipant": True
            }
            leagues.append(data)
        return {
            "is_superuser": False,
            "leagues": leagues
        }


def create_league_for_user(league_data, user):
    """
    Create a new league for a user.
    
    Args:
        league_data: dict with league data (name, etc.)
        user: User object (will become admin)
    
    Returns:
        tuple: (success: bool, response_data: dict, status_code: int)
    """
    serializer = LeaguesSerializer(data=league_data)
    if serializer.is_valid():
        league = serializer.save()
        LeagueParticipant.objects.create(
            league=league,
            user=user,
            current_balance=Decimal('10000.00'),
            leagueAdmin=True
        )
        return True, serializer.data, 201
    return False, {'errors': serializer.errors}, 400


def get_owned_stocks_data(league_id, user):
    """
    Get all owned stocks data for a user in a league.
    
    Args:
        league_id: UUID of the league
        user: User object
    
    Returns:
        tuple: (success: bool, response_data: dict, status_code: int)
    """
    try:
        # Get league and participant first
        league = League.objects.get(league_id=league_id)
        participant = LeagueParticipant.objects.get(league=league, user=user)
        current_balance = float(participant.current_balance)
        
        # Get owned stocks
        owned_stocks = getOwnedStocks(league_id, user)
        stocks = []

        for stock in owned_stocks:
            try:
                data = {
                    "shares": float(stock.shares),
                    "current_price": float(stock.stock.current_price),
                    "start_price": float(stock.stock.start_price),
                    "price_at_start_of_week": float(stock.price_at_start_of_week),
                    "ticker": stock.stock.ticker,
                    "name": stock.stock.name,
                }
                stocks.append(data)
            except Exception as e:
                print(f"Error processing stock {stock.stock.ticker}: {str(e)}")
                continue
        
        # Calculate total stock value
        total_stock_value = getTotalStockValue(league_id, user)
        total_stock_value_float = float(total_stock_value) if total_stock_value is not None else 0.0
        
        return True, {
            "stocks": stocks,
            "current_balance": current_balance,
            "total_stock_value": total_stock_value_float,
            "net_worth": total_stock_value_float + current_balance
        }, 200
        
    except League.DoesNotExist:
        return False, {'error': 'League not found'}, 404
    except LeagueParticipant.DoesNotExist:
        return False, {'error': 'You are not a participant in this league'}, 404
    except Exception as e:
        import traceback
        print(f"Error in get_owned_stocks_data: {str(e)}")
        print(traceback.format_exc())
        return False, {'error': f'An error occurred: {str(e)}'}, 500


def get_stock_info_data(league_id, ticker, user):
    """
    Get stock information for a user in a league.
    
    Args:
        league_id: UUID of the league
        ticker: Stock ticker symbol
        user: User object
    
    Returns:
        tuple: (success: bool, response_data: dict, status_code: int)
    """
    try:
        league = League.objects.get(league_id=league_id)
        participant = LeagueParticipant.objects.get(league=league, user=user)
        stock = Stock.objects.get(ticker=ticker)
        
        # Get owned shares if any
        try:
            user_stock = UserLeagueStock.objects.get(
                league_participant=participant,
                stock=stock
            )
            owned_shares = float(user_stock.shares)
        except UserLeagueStock.DoesNotExist:
            owned_shares = 0
        
        return True, {
            'balance': float(participant.current_balance),
            'owned_shares': owned_shares,
            'current_price': float(stock.current_price)
        }, 200
        
    except League.DoesNotExist:
        return False, {'error': 'League not found'}, 404
    except LeagueParticipant.DoesNotExist:
        return False, {'error': 'You are not a participant in this league'}, 404
    except Stock.DoesNotExist:
        return False, {'error': 'Stock not found'}, 404

