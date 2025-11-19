from django.urls import path
from . import views
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('stocks/', views.ViewAllStocks.as_view(), name="viewAllStocks"),
    path('owned-stocks/<uuid:league_id>/', views.ViewAllOwnedStocks.as_view(), name="viewAllOwnedStocks"),
    path('weekly-profits/<uuid:league_id>/', views.ViewUserWeeklyProfits.as_view(), name="ViewUserWeeklyProfits"),
    path('opponent-weekly-profits/<uuid:league_id>/', views.ViewOpponentWeeklyProfits.as_view(), name="ViewOpponentWeeklyProfits"),
    path('leagues/', views.ViewAllLeagues.as_view(), name="leagues"),
    path('leagues/join/', views.JoinLeagueView.as_view(), name="join_league"),
    path('stocks/buy/', views.BuyStockView.as_view(), name="buy_stock"),
    path('stocks/sell/', views.SellStockView.as_view(), name="sell_stock"),
    path('stocks/info/<uuid:league_id>/<str:ticker>/', views.GetStockInfoView.as_view(), name="get_stock_info"),
    path('leagues/<uuid:league_id>/set-start-date/', views.SetLeagueStartDateView.as_view(), name="set_league_start_date"),
    path('leagues/<uuid:league_id>/schedule/', views.GetParticipantScheduleView.as_view(), name="get_participant_schedule"),
    path('leagues/<uuid:league_id>/leaderboard/', views.GetLeagueLeaderboardView.as_view(), name="get_league_leaderboard"),
    path('leagues/<uuid:league_id>/matchup/', views.GetCurrentMatchupView.as_view(), name="get_current_matchup"),
]