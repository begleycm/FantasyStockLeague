from datetime import timedelta
from django.contrib.auth.models import User 
from rest_framework import serializers
from catalog.models import League, Stock

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}} 

    def create(self, validated_data): 
        user = User.objects.create_user(**validated_data)
        return user

class UpdateUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]
    
    def validate_username(self, value):
        # Check if username already exists (excluding current user)
        if self.instance and User.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["ticker", "name", "start_price", "current_price"]

class LeaguesSerializer(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()
    can_set_start_date = serializers.SerializerMethodField()
    
    class Meta:
        model = League
        fields = ['league_id', 'name', 'start_date', 'end_date', 'participant_count', 'can_set_start_date']
        read_only_fields = ['league_id', 'end_date', 'participant_count', 'can_set_start_date']
    
    def get_participant_count(self, obj):
        return obj.participant_count
    
    def get_can_set_start_date(self, obj):
        return obj.can_set_start_date()
    
    def create(self, validated_data):
        # Remove start_date from validated_data if provided (will be set later)
        validated_data.pop('start_date', None)
        validated_data.pop('end_date', None)
        return super().create(validated_data)