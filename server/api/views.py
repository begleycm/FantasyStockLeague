from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import generics
from api.serializer import LeaguesSerializer, StockSerializer, UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from catalog.models import LeagueParticipant, Stock, UserLeagueStock, League
from api.apiUtils.utils import getCurrentOpponent, getUserWeeklyStockProfits, getOwnedStocks, getTotalStockValue
from api.apiUtils.joinLeague import join_league

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class ViewAllStocks(generics.ListCreateAPIView):
    serializer_class = StockSerializer
    queryset = Stock.objects.all()  
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        stocks = []
        for stock in Stock.objects.all():
            data = {
                "ticker":stock.ticker,
                "name":stock.name,
                "start_price":stock.start_price,
                "current_price":stock.current_price,
            }
            stocks.append(data)
        return Response(stocks)


class ViewAllOwnedStocks(generics.ListCreateAPIView):
    #serializer_class = UserLeagueStockSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, league_id, format=None):
        from api.apiUtils.leagueUtils import get_owned_stocks_data
        
        success, response_data, status_code = get_owned_stocks_data(league_id, request.user)
        return Response(response_data, status=status_code)


class GetStockInfoView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, league_id, ticker, format=None):
        from api.apiUtils.leagueUtils import get_stock_info_data
        
        success, response_data, status_code = get_stock_info_data(league_id, ticker, request.user)
        return Response(response_data, status=status_code)

class ViewUserWeeklyProfits(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, league_id, format=None):
        stocks = getUserWeeklyStockProfits(league_id, request.user)
        return Response(stocks)

class ViewOpponentWeeklyProfits(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, league_id, format=None):
        stocks = getUserWeeklyStockProfits(league_id, getCurrentOpponent(league_id, request.user))
        return Response(stocks)
        
class LeagueView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    # Viewing Data in a league
    def get(self, request, league_id):
        current_league = League.objects.get(league_id=league_id)
        league_participants = LeagueParticipant.objects.get(League=current_league)
        leagueUserData = []
        for league_participant in league_participants:
            total_profit = 0
            for stock in getOwnedStocks(league_id, league_participant.user):
                total_profit += (stock.price_at_start_of_week - stock.stock.current_price) * stock.shares
            data = {
                "user":league_participant.user,
                "wins":league_participant.wins,
                "losses":league_participant.losses,
                "net_worth": getTotalStockValue(league_id, league_participant.user) + league_participant.current_balance,
                "weekly_profit": total_profit,
            }
            leagueUserData.append(data)
        return Response(leagueUserData)

class ViewAllLeagues(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = League.objects.all()
    serializer_class = LeaguesSerializer

    def get(self, request, *args, **kwargs):
        from api.apiUtils.leagueUtils import get_user_leagues_data
        
        response_data = get_user_leagues_data(request.user)
        return Response(response_data)
    
    def post(self, request, *args, **kwargs):
        from api.apiUtils.leagueUtils import create_league_for_user
        
        success, response_data, status_code = create_league_for_user(request.data, request.user)
        return Response(response_data, status=status_code)


class JoinLeagueView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            league_id = request.data.get('league_id')
            success, response_data, status_code = join_league(league_id, request.user)
            return Response(response_data, status=status_code)
        except Exception as e:
            import traceback
            print(f"Error joining league: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)



class BuyStockView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            from api.apiUtils.buySellStock import buy_stock
            
            league_id = request.data.get('league_id')
            ticker = request.data.get('ticker')
            shares = request.data.get('shares')
            
            if not league_id or not ticker or not shares:
                return Response({'error': 'league_id, ticker, and shares are required'}, status=400)
            
            success, response_data, status_code = buy_stock(league_id, request.user, ticker, shares)
            return Response(response_data, status=status_code)
        except Exception as e:
            import traceback
            print(f"Error buying stock: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)


class SellStockView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            from api.apiUtils.buySellStock import sell_stock
            
            league_id = request.data.get('league_id')
            ticker = request.data.get('ticker')
            shares = request.data.get('shares')
            
            if not league_id or not ticker or not shares:
                return Response({'error': 'league_id, ticker, and shares are required'}, status=400)
            
            success, response_data, status_code = sell_stock(league_id, request.user, ticker, shares)
            return Response(response_data, status=status_code)
        except Exception as e:
            import traceback
            print(f"Error selling stock: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)


class GetLeagueLeaderboardView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, league_id, format=None):
        """Get the leaderboard for a league sorted by wins/losses and net worth"""
        try:
            from api.apiUtils.matchupUtils import get_league_leaderboard_data
            
            league = League.objects.get(league_id=league_id)
            
            # Verify user is a participant
            try:
                user_participant = LeagueParticipant.objects.get(league=league, user=request.user)
            except LeagueParticipant.DoesNotExist:
                return Response({'error': 'You are not a participant in this league'}, status=404)
            
            leaderboard_data = get_league_leaderboard_data(league, league_id, user_participant)
            return Response(leaderboard_data, status=200)
            
        except League.DoesNotExist:
            return Response({'error': 'League not found'}, status=404)
        except Exception as e:
            import traceback
            print(f"Error getting league leaderboard: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)


class GetParticipantScheduleView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, league_id, format=None):
        """Get the schedule for the current user in a specific league"""
        try:
            from api.apiUtils.matchupUtils import get_participant_schedule_data
            
            league = League.objects.get(league_id=league_id)
            participant = LeagueParticipant.objects.get(league=league, user=request.user)
            
            schedule_data = get_participant_schedule_data(league, participant)
            return Response(schedule_data, status=200)
            
        except League.DoesNotExist:
            return Response({'error': 'League not found'}, status=404)
        except LeagueParticipant.DoesNotExist:
            return Response({'error': 'You are not a participant in this league'}, status=404)
        except Exception as e:
            import traceback
            print(f"Error getting participant schedule: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)


class SetLeagueStartDateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, league_id, *args, **kwargs):
        """Set start date for a league (requires 8 participants and league admin)"""
        try:
            from api.apiUtils.matchupUtils import validate_and_set_start_date
            
            league = League.objects.get(league_id=league_id)
            
            # Get start_date from request
            start_date = request.data.get('start_date')
            if not start_date:
                return Response({'error': 'start_date is required'}, status=400)
            
            success, response_data, status_code = validate_and_set_start_date(league, start_date, request.user)
            return Response(response_data, status=status_code)
            
        except League.DoesNotExist:
            return Response({'error': 'League not found'}, status=404)
        except Exception as e:
            import traceback
            print(f"Error setting league start date: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)


class GetCurrentMatchupView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, league_id, format=None):
        """Get the current matchup for the user in a specific league"""
        try:
            from api.apiUtils.matchupUtils import get_current_matchup_data
            
            league = League.objects.get(league_id=league_id)
            
            # Verify user is a participant
            try:
                user_participant = LeagueParticipant.objects.get(league=league, user=request.user)
            except LeagueParticipant.DoesNotExist:
                return Response({'error': 'You are not a participant in this league'}, status=404)
            
            matchup_data = get_current_matchup_data(league, league_id, request.user)
            
            # Check if there's an error in the response
            if 'error' in matchup_data:
                status_code = 400 if 'not started' in matchup_data['error'] or 'No matchup' in matchup_data['error'] else 404
                return Response(matchup_data, status=status_code)
            
            return Response(matchup_data, status=200)
            
        except League.DoesNotExist:
            return Response({'error': 'League not found'}, status=404)
        except Exception as e:
            import traceback
            print(f"Error getting current matchup: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)

