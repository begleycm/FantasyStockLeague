from decimal import Decimal
import uuid
from datetime import date, timedelta
from rest_framework.response import Response
from catalog.models import League, LeagueParticipant
from api.serializer import LeaguesSerializer


def join_league(league_id, user):
    """
    Utility function to join a league.
    Automatically sets start_date and end_date when 8 participants are reached.
    Returns a tuple: (success: bool, response_data: dict, status_code: int)
    """
    if not league_id:
        return False, {'error': 'league_id is required'}, 400
    
    # Validate and convert league_id to UUID if it's a string
    try:
        if isinstance(league_id, str):
            league_id = uuid.UUID(league_id)
    except (ValueError, TypeError):
        return False, {'error': 'Invalid league_id format'}, 400
    
    # Get the league
    try:
        league = League.objects.get(league_id=league_id)
    except League.DoesNotExist:
        return False, {'error': 'League not found'}, 404
    
    # Check if user is already in the league
    existing_participant = LeagueParticipant.objects.filter(
        league=league,
        user=user
    ).first()
    
    if existing_participant:
        return False, {'error': 'You are already a member of this league'}, 400
    
    # Check if league is full (max 8 participants)
    current_participant_count = LeagueParticipant.objects.filter(league=league).count()
    if current_participant_count >= 8:
        return False, {'error': 'This league is full (maximum 8 participants)'}, 400
    
    # Create LeagueParticipant entry
    try:
        participant = LeagueParticipant.objects.create(
            league=league,
            user=user,
            current_balance=Decimal('10000.00'),
            leagueAdmin=False
        )
        
        # Check if league now has 8 participants and automatically set start/end dates
        updated_participant_count = LeagueParticipant.objects.filter(league=league).count()
        if updated_participant_count == 8 and not league.start_date:
            # Set start date to today
            today = date.today()
            # Set end date to 8 weeks (56 days) from start date
            end_date = today + timedelta(weeks=8)
            
            league.start_date = today
            league.end_date = end_date
            league.save()
        
        # Serialize league data for response
        serializer = LeaguesSerializer(league)
        return True, {
            'message': 'Successfully joined league',
            'league': serializer.data
        }, 201
    except Exception as e:
        return False, {'error': f'Failed to join league: {str(e)}'}, 500
