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


# Cache for all stocks data (30-minute cooldown)
_stocks_cache = None
_stocks_cache_timestamp = None
CACHE_DURATION = 30 * 60  # 30 minutes in seconds

def _get_cached_all_stocks():
    """Get cached all stocks data if still valid, otherwise None."""
    global _stocks_cache, _stocks_cache_timestamp
    import time
    
    if _stocks_cache is not None and _stocks_cache_timestamp is not None:
        age = time.time() - _stocks_cache_timestamp
        if age < CACHE_DURATION:
            return _stocks_cache
        else:
            # Cache expired
            _stocks_cache = None
            _stocks_cache_timestamp = None
    return None

def _update_all_stocks_cache():
    """Update all stocks and cache the data."""
    global _stocks_cache, _stocks_cache_timestamp
    import time
    import update_stocks as update_stocks_module
    from catalog.models import Stock
    
    # Always update stocks before caching
    try:
        update_stocks_module.update_stocks(force=True)
    except Exception:
        pass  # Continue even if update fails
    
    # Get all stocks from database
    stock_queryset = Stock.objects.all()
    stocks_data = {}
    
    for stock in stock_queryset:
        try:
            current = float(stock.current_price) if stock.current_price else 0.0
            start = float(stock.start_price) if stock.start_price else 0.0
            
            # Calculate daily change
            if start > 0:
                daily_change = current - start
                try:
                    daily_change_percent = (daily_change / start) * 100 if start != 0 else None
                except Exception:
                    daily_change_percent = None
            else:
                daily_change = None
                daily_change_percent = None
            
            stocks_data[stock.ticker] = {
                "ticker": stock.ticker,
                "name": stock.name,
                "start_price": start,
                "current_price": current,
                "daily_change": daily_change,
                "daily_change_percent": daily_change_percent,
            }
        except Exception:
            continue
    
    # Cache the data
    _stocks_cache = stocks_data
    _stocks_cache_timestamp = time.time()
    
    return stocks_data

def get_owned_stocks_data(league_id, user):
    """
    Get all owned stocks data for a user in a league.
    Uses cached all stocks data (30-minute cooldown) to ensure prices align with explore stocks.
    
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
        
        # Get cached all stocks data (or update if cache expired)
        cached_stocks = _get_cached_all_stocks()
        if cached_stocks is None:
            # Cache expired or doesn't exist, update and cache
            all_stocks_data = _update_all_stocks_cache()
        else:
            # Use cached data
            all_stocks_data = cached_stocks
        
        # Get owned stocks from database (always fresh from DB)
        owned_stocks = getOwnedStocks(league_id, user)
        stocks = []

        for stock in owned_stocks:
            try:
                ticker = stock.stock.ticker
                
                # Get stock data from cache (ensures prices align with explore stocks)
                stock_data = all_stocks_data.get(ticker, {})
                
                # Merge cached stock data with owned stock details from DB
                data = {
                    "shares": float(stock.shares),
                    "avg_price_per_share": float(stock.avg_price_per_share),
                    "ticker": ticker,
                    "name": stock_data.get("name", stock.stock.name),
                    "current_price": stock_data.get("current_price", float(stock.stock.current_price)),
                    "start_price": stock_data.get("start_price", float(stock.stock.start_price)),
                    "daily_change": stock_data.get("daily_change"),
                    "daily_change_percent": stock_data.get("daily_change_percent"),
                }
                stocks.append(data)
            except Exception as e:
                print(f"Error processing stock {stock.stock.ticker}: {str(e)}")
                continue
        
        # Calculate total stock value using cached prices
        total_stock_value = 0.0
        for stock in owned_stocks:
            try:
                ticker = stock.stock.ticker
                stock_data = all_stocks_data.get(ticker, {})
                current_price = stock_data.get("current_price", float(stock.stock.current_price))
                total_stock_value += current_price * float(stock.shares)
            except Exception:
                continue
        
        return True, {
            "stocks": stocks,
            "current_balance": current_balance,
            "total_stock_value": total_stock_value,
            "net_worth": total_stock_value + current_balance
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

