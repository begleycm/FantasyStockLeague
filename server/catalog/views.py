from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotFound, HttpResponse
from django.urls import path, reverse
import os
import requests
from dotenv import load_dotenv
from datetime import date

from catalog.stock_utils import get_current_stock_price, get_profit_float, get_stock_closing_price
from catalog.models import LeagueParticipant, Matchup
from django.db import models

def response_not_found_view(request, exception=None):
    return HttpResponseNotFound("Page not found", status=404)

# redefine 404 error variable to our custom page
handler404 = response_not_found_view
load_dotenv()

api_key = os.getenv("STOCK_API_KEY")

def get_absolute_url(self):
    """Returns the url to access a particular genre instance."""
    return reverse('stock-detail', args=[str(self.id)])
    

def get_daily_closing_price(ticker: str, start_date: str):
    """Returns the daily closing performance of a stock. Start date must be in the format
    'year-month-day' with leading 0s as needed. ex: '2025-06-23'"""
    return get_stock_closing_price(ticker, start_date)
    
        
def get_current_price(ticker: str):
    """Returns the current price of a stock."""
    return get_current_stock_price(ticker)
        

def get_stock_profit(ticker: str, start_date: str):
    """Returns the current profit (as a float) of a stock since a start date. Start date should be
    In the format year-month-day ex: '2025-06-23'"""
    return get_profit_float(ticker, start_date)


def create_league_schedule(league):
    """Creates a round robin league schedule that is 7 weeks long with 8 participants.
    Returns created matchups as a list of matchups.
    
    Throws a ValueError is the league is an incorrect number of participants."""
    participants = list(LeagueParticipant.objects.filter(league=league))
    
    # Check to see if league is correct length(8)
    if len(participants) != 8:
        raise ValueError(f"League must have 8 participants.")
    
    Matchup.objects.filter(league=league).delete()
    created_matchups = []
    
    # Round robin schedule, each participant faces another 1 time
    schedule = [
        [(0, 7), (1, 6), (2, 5), (3, 4)],
        [(0, 6), (7, 5), (1, 4), (2, 3)],
        [(0, 5), (6, 4), (7, 3), (1, 2)],
        [(0, 4), (5, 3), (6, 2), (7, 1)],
        [(0, 3), (4, 2), (5, 1), (6, 7)],
        [(0, 2), (3, 1), (4, 7), (5, 6)],
        [(0, 1), (2, 7), (3, 6), (4, 5)]
    ]
    
    # Create matchups for each week
    for week_num, week_matchups in enumerate(schedule, start=1):
        for participant1_id, participant2_id in week_matchups:
            matchup = Matchup.objects.create(
                league=league,
                week_number=week_num,
                participant1=participants[participant1_id],
                participant2=participants[participant2_id],
                start_of_week_net_worth1=0.00,
                start_of_week_net_worth2=0.00
            )
            created_matchups.append(matchup)
    return created_matchups


def get_league_schedule(league):
    """
    Gets the schedule for a specific league organized by week.
        
    Returns a Dictionary with week numbers as keys and lists of matchups as values
    Example: {1: [matchup1, matchup2, ...], 2: [...], ...}
    """
    matchups = Matchup.objects.filter(league=league).order_by('week_number')
    
    schedule = {}
    for matchup in matchups:
        week = matchup.week_number
        if week not in schedule:
            schedule[week] = []
        schedule[week].append(matchup)
    
    return schedule


def get_participant_schedule(participant: LeagueParticipant):
    """
    Gets all matchups for a specific participant across all weeks.
        
    Returns a list of Matchup objects ordered by week
    """
    matchups = Matchup.objects.filter(
        league=participant.league
    ).filter(
        models.Q(participant1=participant) | models.Q(participant2=participant)
    ).order_by('week_number')
    
    return list(matchups)
