from datetime import timezone
import uuid
from django.db import models

# Create your models here.
from django.forms import ValidationError
from django.urls import reverse # Used in get_absolute_url() to get URL for specified ID

from django.db.models import UniqueConstraint # Constrains fields to unique values
from django.db.models.functions import Lower # Returns lower cased value of field
from django.contrib.auth.models import User # Use django user
    
class Stock(models.Model):
    """Model representing a specific stock."""
    # Ticker as primary key
    ticker = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=200)
    start_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Yesterday's closing price (updated daily)")
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.ticker} - {self.name}"
    
    @property
    def profit(self):
        return (self.current_price - self.start_price) * self.shares


class ApiCallTracker(models.Model):
    """Singleton model to track API call limits (max 5 calls per 30 minutes)."""
    id = models.IntegerField(primary_key=True, default=1, editable=False)
    api_call_count = models.IntegerField(default=0, help_text="Number of API calls in current window")
    window_start_time = models.DateTimeField(null=True, blank=True, help_text="Start time of current 30-minute window")
    last_api_call_time = models.DateTimeField(null=True, blank=True, help_text="Timestamp of the last API call")
    
    class Meta:
        verbose_name = "API Call Tracker"
        verbose_name_plural = "API Call Tracker"
    
    def __str__(self):
        return f"API Calls: {self.api_call_count}/5 (Window started: {self.window_start_time})"
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance."""
        instance, created = cls.objects.get_or_create(id=1)
        return instance
    
    
class League(models.Model):
    """Model representing the settings for the league"""
    league_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, default="Trading League")
    start_date = models.DateField(null=True, blank=True) # Set once 8 participants join
    end_date = models.DateField(null=True, blank=True) # Autopopulated (8 weeks after start day)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.league_id})"
    
    def clean(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date")


    @property
    def is_ongoing(self):
        if not self.start_date or not self.end_date:
            return False
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
    
    @property
    def participant_count(self):
        """Get the number of participants in the league"""
        return self.participants.count()
    
    def can_set_start_date(self):
        """Check if league has 8 participants and can set start date f"""
        return self.participant_count >= 8


class LeagueParticipant(models.Model):
    """Links users to leagues and tracks their performance"""
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='league_participations')
    current_balance = models.DecimalField(max_digits=12, decimal_places=2)
    wins = models.CharField(max_length=100, blank=True, null=True)  
    losses = models.CharField(max_length=100, blank=True, null=True)
    leagueAdmin = models.BooleanField(default=False)  

    class Meta:
        unique_together = ['league', 'user']
    
    def __str__(self):
        return f"{self.user.username} in {self.league.name}"

class UserLeagueStock(models.Model):
    """Links league participant to a stock"""
    league_participant = models.ForeignKey(LeagueParticipant, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
 
    avg_price_per_share = models.DecimalField(decimal_places=2, default=0.00, max_digits=10)  # Average purchase price
    shares = models.DecimalField(decimal_places=2, default=0.01, max_digits=10)

    def __str__(self):
        return f"{self.league_participant} in {self.stock}"
    
    
    @property
    def total_profit(self):
        """Calculate total profit based on average purchase price vs current price"""
        if self.avg_price_per_share == 0:
            return 0
        return (self.stock.current_price - self.avg_price_per_share) * self.shares
