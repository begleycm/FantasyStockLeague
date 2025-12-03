from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import generics
from api.serializer import LeaguesSerializer, StockSerializer, UserSerializer, UpdateUsernameSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from catalog.models import LeagueParticipant, Stock, UserLeagueStock, League
from api.apiUtils.utils import getUserStockProfits, getOwnedStocks, getTotalStockValue
from api.apiUtils.joinLeague import join_league
from datetime import date, timedelta
from catalog.views import get_daily_closing_price
from catalog.stock_populator import update_stock_prices
import update_stocks as update_stocks_module

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class ViewAllStocks(generics.ListCreateAPIView):
    serializer_class = StockSerializer
    queryset = Stock.objects.all()  
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        # Get stocks from database first (before any updates)
        stock_queryset = Stock.objects.all()
        
        # If no stocks exist, return empty list immediately
        if not stock_queryset.exists():
            return Response([], status=200)
        
        # Always update stocks before returning data
        try:
            update_stocks_module.update_stocks(force=True)
        except Exception:
            # Don't fail the request if update logic errors — just log and continue
            # We'll return the existing data from the database
            pass

        # Refresh the queryset to get updated prices
        stock_queryset = Stock.objects.all()
        stocks = []
        
        for stock in stock_queryset:
            try:
                # Ensure we have valid numeric values
                current = float(stock.current_price) if stock.current_price else 0.0
                start = float(stock.start_price) if stock.start_price else 0.0
            except (ValueError, TypeError):
                current = 0.0
                start = 0.0

            # Calculate daily change based on start_price (which is yesterday's closing price)
            if start > 0:
                daily_change = current - start
                try:
                    daily_change_percent = (daily_change / start) * 100 if start != 0 else None
                except Exception:
                    daily_change_percent = None
            else:
                daily_change = None
                daily_change_percent = None

            data = {
                "ticker": stock.ticker,
                "name": stock.name,
                "start_price": start,  # Yesterday's closing price (updated daily)
                "current_price": current,  # Current price
                "daily_change": daily_change,
                "daily_change_percent": daily_change_percent,
            }
            stocks.append(data)

        # Always return the stocks data, even if empty
        return Response(stocks, status=200)


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
        
class LeagueView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    # Viewing Data in a league
    def get(self, request, league_id):
        current_league = League.objects.get(league_id=league_id)
        league_participants = LeagueParticipant.objects.get(League=current_league)
        leagueUserData = []
        for league_participant in league_participants:
            data = {
                "user":league_participant.user.username,
                "net_worth": getTotalStockValue(league_id, league_participant.user) + float(league_participant.current_balance),
            }
            leagueUserData.append(data)
        # Sort by net worth descending
        leagueUserData.sort(key=lambda x: x['net_worth'], reverse=True)
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
        """Get the leaderboard for a league sorted by net worth"""
        try:
            league = League.objects.get(league_id=league_id)
            
            # Verify user is a participant
            try:
                user_participant = LeagueParticipant.objects.get(league=league, user=request.user)
            except LeagueParticipant.DoesNotExist:
                return Response({'error': 'You are not a participant in this league'}, status=404)
            
            # Get all participants
            participants = league.participants.all()
            
            leaderboard_data = []
            for participant in participants:
                net_worth = getTotalStockValue(league_id, participant.user) + float(participant.current_balance)
                leaderboard_data.append({
                    'username': participant.user.username,
                    'net_worth': round(net_worth, 2),
                    'is_current_user': participant == user_participant,
                })
            
            # Sort by net worth descending
            leaderboard_data.sort(key=lambda x: x['net_worth'], reverse=True)
            
            return Response({'leaderboard': leaderboard_data}, status=200)
            
        except League.DoesNotExist:
            return Response({'error': 'League not found'}, status=404)
        except Exception as e:
            import traceback
            print(f"Error getting league leaderboard: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)


class SetLeagueStartDateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, league_id, *args, **kwargs):
        """Set start date and end date for a league (requires league admin)"""
        try:
            from datetime import datetime
            from catalog.models import LeagueParticipant
            
            league = League.objects.get(league_id=league_id)
            
            # Check if user is a participant and admin
            try:
                participant = LeagueParticipant.objects.get(league=league, user=request.user)
                if not participant.leagueAdmin:
                    return Response({'error': 'Only league admins can set dates'}, status=403)
            except LeagueParticipant.DoesNotExist:
                return Response({'error': 'You are not a participant in this league'}, status=404)
            
            # Get start_date and end_date from request
            start_date_str = request.data.get('start_date')
            end_date_str = request.data.get('end_date')
            
            if not start_date_str:
                return Response({'error': 'start_date is required'}, status=400)
            if not end_date_str:
                return Response({'error': 'end_date is required'}, status=400)
            
            # Parse dates
            try:
                start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
            
            # Validate dates
            if end_date_obj <= start_date_obj:
                return Response({'error': 'End date must be after start date'}, status=400)
            
            today = datetime.now().date()
            if start_date_obj < today:
                return Response({'error': 'Start date cannot be in the past'}, status=400)
            
            # Set dates
            league.start_date = start_date_obj
            league.end_date = end_date_obj
            league.save()
            
            from api.serializer import LeaguesSerializer
            serializer = LeaguesSerializer(league)
            return Response({
                'message': 'League dates set successfully',
                'league': serializer.data
            }, status=200)
            
        except League.DoesNotExist:
            return Response({'error': 'League not found'}, status=404)
        except Exception as e:
            import traceback
            print(f"Error setting league dates: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)


class DeleteLeagueView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, league_id, *args, **kwargs):
        """Delete a league (requires league admin or superuser)"""
        try:
            league = League.objects.get(league_id=league_id)
            
            # Check if user is superuser - superusers can delete any league
            if request.user.is_superuser:
                league_name = league.name
                league.delete()
                return Response({
                    'message': f'League "{league_name}" deleted successfully'
                }, status=200)
            
            # Check if user is a participant and admin
            try:
                participant = LeagueParticipant.objects.get(league=league, user=request.user)
                if not participant.leagueAdmin:
                    return Response({'error': 'Only league admins can delete leagues'}, status=403)
                
                # Admin can delete their league
                league_name = league.name
                league.delete()
                return Response({
                    'message': f'League "{league_name}" deleted successfully'
                }, status=200)
            except LeagueParticipant.DoesNotExist:
                return Response({'error': 'You are not a participant in this league'}, status=404)
            
        except League.DoesNotExist:
            return Response({'error': 'League not found'}, status=404)
        except Exception as e:
            import traceback
            print(f"Error deleting league: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)


class UpdateUsernameView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUsernameSerializer

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        """Update the current user's username"""
        try:
            user = self.get_object()
            serializer = self.get_serializer(user, data=request.data, partial=False)
            
            if serializer.is_valid():
                old_username = user.username
                serializer.save()
                new_username = user.username
                
                return Response({
                    'message': 'Username updated successfully',
                    'username': new_username
                }, status=200)
            else:
                return Response({
                    'error': 'Invalid data',
                    'errors': serializer.errors
                }, status=400)
                
        except Exception as e:
            import traceback
            print(f"Error updating username: {str(e)}")
            print(traceback.format_exc())
            return Response({'error': f'An error occurred: {str(e)}'}, status=500)

