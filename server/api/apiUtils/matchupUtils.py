from datetime import date, datetime, timedelta
from api.apiUtils.utils import getTotalStockValue
from catalog.views import get_participant_schedule, create_league_schedule
from catalog.models import Matchup
from django.db.models import Q
from api.serializer import LeaguesSerializer


def calculate_current_week(league):
    """
    Calculate the current week number for a league.
    Returns None if league hasn't started, or the week number (1-7) if it has.
    """
    if not league.start_date:
        return None
    
    today = date.today()
    if today < league.start_date:
        return 0  # League hasn't started yet
    
    days_since_start = (today - league.start_date).days
    current_week = min((days_since_start // 7) + 1, 7)  # Cap at 7 weeks
    
    # If it's past the end date, use week 7
    if league.end_date and today > league.end_date:
        current_week = 7
    
    return current_week


def determine_matchup_winner(matchup, league, league_id, current_week):
    """
    Determine winner for a matchup based on net worth comparison for completed weeks.
    
    Args:
        matchup: Matchup object
        league: League object
        league_id: UUID of the league
        current_week: Current week number (from calculate_current_week)
    
    Returns:
        LeagueParticipant object if winner can be determined, None otherwise
    """
    if matchup.winner:
        return matchup.winner  # Already determined
    
    # Only determine winners for completed weeks (weeks that have ended)
    # A week is completed if it's before the current week
    if not league.start_date or current_week is None:
        return None  # League hasn't started yet
    if matchup.week_number >= current_week:
        return None  # Week hasn't ended yet, can't determine winner
    
    # Calculate current net worth for both participants
    # Note: Ideally we'd use end-of-week net worth, but since we don't store that,
    # we use current net worth as a proxy
    net_worth1 = getTotalStockValue(league_id, matchup.participant1.user) + float(matchup.participant1.current_balance)
    net_worth2 = getTotalStockValue(league_id, matchup.participant2.user) + float(matchup.participant2.current_balance)
    
    # Determine winner based on higher net worth
    if net_worth1 > net_worth2:
        return matchup.participant1
    elif net_worth2 > net_worth1:
        return matchup.participant2
    else:
        # Tie - could use tiebreaker, for now return None (no winner)
        return None


def get_participant_schedule_data(league, participant):
    """
    Get schedule data for a participant in a league.
    
    Args:
        league: League object
        participant: LeagueParticipant object
    
    Returns:
        dict with schedule data, current_week, and league dates
    """
    # Get all matchups for this participant
    matchups = get_participant_schedule(participant)
    
    # Calculate current week if league has started
    current_week = calculate_current_week(league)
    
    # Format matchups for response
    schedule_data = []
    for matchup in matchups:
        # Determine opponent
        if matchup.participant1 == participant:
            opponent = matchup.participant2
        else:
            opponent = matchup.participant1
        
        schedule_data.append({
            'week_number': matchup.week_number,
            'opponent_username': opponent.user.username,
            'opponent_id': opponent.id,
            'is_current_week': current_week is not None and matchup.week_number == current_week,
            'winner_id': matchup.winner.id if matchup.winner else None,
            'is_winner': matchup.winner == participant if matchup.winner else None,
        })
    
    return {
        'schedule': schedule_data,
        'current_week': current_week,
        'league_start_date': league.start_date.isoformat() if league.start_date else None,
        'league_end_date': league.end_date.isoformat() if league.end_date else None,
    }


def validate_and_set_start_date(league, start_date_str, user):
    """
    Validate and set the start date for a league.
    
    Args:
        league: League object
        start_date_str: Start date string in YYYY-MM-DD format
        user: User object (to check if admin)
    
    Returns:
        tuple: (success: bool, response_data: dict, status_code: int)
    """
    from catalog.models import LeagueParticipant
    
    # Check if user is a participant and admin
    try:
        participant = LeagueParticipant.objects.get(league=league, user=user)
        if not participant.leagueAdmin:
            return False, {'error': 'Only league admins can set the start date'}, 403
    except LeagueParticipant.DoesNotExist:
        return False, {'error': 'You are not a participant in this league'}, 404
    
    # Check if league has 8 participants
    participant_count = league.participant_count
    if participant_count < 8:
        return False, {
            'error': f'League must have 8 participants before setting start date. Currently has {participant_count} participants.'
        }, 400
    
    # Parse start date
    try:
        start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except ValueError:
        return False, {'error': 'Invalid date format. Use YYYY-MM-DD'}, 400
    
    # Validate that the date is a Monday (0 = Monday in Python's weekday())
    if start_date_obj.weekday() != 0:
        return False, {'error': 'Start date must be a Monday'}, 400
    
    # Calculate the next Monday (or later if today is Monday)
    today = date.today()
    today_weekday = today.weekday()  # 0 = Monday, 6 = Sunday
    
    if today_weekday == 6:  # Sunday
        days_until_monday = 1
    elif today_weekday == 0:  # Monday
        days_until_monday = 7  # Next Monday
    else:  # Tuesday through Saturday
        days_until_monday = 8 - today_weekday
    
    next_monday = today + timedelta(days=days_until_monday)
    
    # Validate that the start date is the next Monday or later
    if start_date_obj < next_monday:
        return False, {
            'error': f'Start date must be the next Monday ({next_monday.strftime("%Y-%m-%d")}) or later'
        }, 400
    
    # Set start and end dates
    league.start_date = start_date_obj
    league.end_date = start_date_obj + timedelta(weeks=7)
    league.save()
    
    # Create league schedule - this is mandatory when setting start date
    try:
        created_matchups = create_league_schedule(league)
        schedule_message = f'Schedule created successfully with {len(created_matchups)} matchups'
    except ValueError as e:
        # This should not happen since we already validated 8 participants
        return False, {
            'error': f'Failed to create league schedule: {str(e)}'
        }, 400
    except Exception as e:
        # Any other error creating schedule
        import traceback
        print(f"Error creating league schedule: {str(e)}")
        print(traceback.format_exc())
        return False, {
            'error': f'Failed to create league schedule: {str(e)}'
        }, 500
    
    serializer = LeaguesSerializer(league)
    return True, {
        'message': 'Start date set successfully and league schedule created',
        'schedule_info': schedule_message,
        'league': serializer.data
    }, 200


def get_league_leaderboard_data(league, league_id, user_participant):
    """
    Get leaderboard data for a league sorted by wins/losses and net worth.
    
    Args:
        league: League object
        league_id: UUID of the league
        user_participant: LeagueParticipant object for the current user
    
    Returns:
        dict with leaderboard data sorted by wins and net worth
    """
    # Get all participants
    participants = league.participants.all()
    
    # Calculate current week if league has started
    current_week = calculate_current_week(league)
    
    leaderboard_data = []
    for participant in participants:
        # Get all matchups for this participant
        participant_matchups = Matchup.objects.filter(
            league=league
        ).filter(
            Q(participant1=participant) | Q(participant2=participant)
        )
        
        wins = 0
        losses = 0
        
        # Calculate wins and losses by determining winners for each matchup
        for matchup in participant_matchups:
            winner = determine_matchup_winner(matchup, league, league_id, current_week)
            
            # Update winner in database if not set (for future reference)
            if not matchup.winner and winner:
                matchup.winner = winner
                matchup.save()
            
            if winner == participant:
                wins += 1
            elif winner is not None:  # There's a winner but it's not this participant
                losses += 1
            # If winner is None (tie or week not completed), don't count as win or loss
        
        # Calculate net worth
        net_worth = getTotalStockValue(league_id, participant.user) + float(participant.current_balance)
        
        leaderboard_data.append({
            'username': participant.user.username,
            'wins': wins,
            'losses': losses,
            'net_worth': round(net_worth, 2),
            'is_current_user': participant == user_participant,
        })
    
    # Sort by wins (descending), then by net worth (descending)
    leaderboard_data.sort(key=lambda x: (x['wins'], x['net_worth']), reverse=True)
    
    return {
        'leaderboard': leaderboard_data
    }


def get_current_matchup_data(league, league_id, user):
    """
    Get current matchup data for a user in a league.
    
    Args:
        league: League object
        league_id: UUID of the league
        user: User object
    
    Returns:
        dict with matchup data including week_number, player1, and player2
    """
    from catalog.models import LeagueParticipant
    from api.apiUtils.utils import getUserWeeklyStockProfits, getTotalStockValue, getOwnedStocks
    
    # Get current week
    current_week = calculate_current_week(league)
    
    if current_week is None or current_week == 0:
        return {
            'error': 'League has not started yet'
        }
    
    # Get user's participant record
    try:
        user_participant = LeagueParticipant.objects.get(league=league, user=user)
    except LeagueParticipant.DoesNotExist:
        return {
            'error': 'You are not a participant in this league'
        }
    
    # Find current matchup
    matchup = Matchup.objects.filter(
        league=league,
        week_number=current_week
    ).filter(
        Q(participant1=user_participant) | Q(participant2=user_participant)
    ).first()
    
    if not matchup:
        return {
            'error': 'No matchup found for current week'
        }
    
    # Determine which participant is player1 and which is player2
    # We'll make the current user player1
    if matchup.participant1 == user_participant:
        participant1 = matchup.participant1
        participant2 = matchup.participant2
    else:
        participant1 = matchup.participant2
        participant2 = matchup.participant1
    
    # Calculate wins and losses for both participants
    def calculate_wins_losses(participant):
        participant_matchups = Matchup.objects.filter(
            league=league
        ).filter(
            Q(participant1=participant) | Q(participant2=participant)
        )
        
        wins = 0
        losses = 0
        
        for m in participant_matchups:
            winner = determine_matchup_winner(m, league, league_id, current_week)
            if winner == participant:
                wins += 1
            elif winner is not None:
                losses += 1
        
        return wins, losses
    
    wins1, losses1 = calculate_wins_losses(participant1)
    wins2, losses2 = calculate_wins_losses(participant2)
    
    # Get net worth for both participants
    net_worth1 = getTotalStockValue(league_id, participant1.user) + float(participant1.current_balance)
    net_worth2 = getTotalStockValue(league_id, participant2.user) + float(participant2.current_balance)
    
    # Get weekly profits for both participants
    weekly_profits1 = getUserWeeklyStockProfits(league_id, participant1.user)
    weekly_profits2 = getUserWeeklyStockProfits(league_id, participant2.user)
    
    # Calculate total weekly profit
    total_weekly_profit1 = sum(stock.get('weekly_profit', 0) for stock in weekly_profits1)
    total_weekly_profit2 = sum(stock.get('weekly_profit', 0) for stock in weekly_profits2)
    
    # Format stocks data for player1
    stocks1 = []
    for stock in weekly_profits1:
        stocks1.append({
            'ticker': stock.get('ticker', ''),
            'profit': round(float(stock.get('weekly_profit', 0)), 2)
        })
    
    # Format stocks data for player2
    stocks2 = []
    for stock in weekly_profits2:
        stocks2.append({
            'ticker': stock.get('ticker', ''),
            'profit': round(float(stock.get('weekly_profit', 0)), 2)
        })
    
    return {
        'week_number': current_week,
        'player1': {
            'name': participant1.user.username,
            'value': round(net_worth1, 2),
            'profit': round(total_weekly_profit1, 2),
            'record': f"{wins1}-{losses1}",
            'stocks': stocks1
        },
        'player2': {
            'name': participant2.user.username,
            'value': round(net_worth2, 2),
            'profit': round(total_weekly_profit2, 2),
            'record': f"{wins2}-{losses2}",
            'stocks': stocks2
        }
    }