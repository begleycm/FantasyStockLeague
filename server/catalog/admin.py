from django.contrib import admin

from .models import Stock, League, LeagueParticipant, UserLeagueStock

admin.site.register(Stock)
admin.site.register(League)
admin.site.register(LeagueParticipant)
admin.site.register(UserLeagueStock)
