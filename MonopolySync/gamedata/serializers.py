from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from .models import UserStat

class UserStatSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    win_percent = serializers.SerializerMethodField()

    class Meta:
        model = UserStat
        fields = ['username', 'games', 'wins', 'win_percent', 'points']

    def get_win_percent(self, obj):
        if obj.games == 0:
            return 0
        return round((obj.wins / obj.games) * 100, 1)

class GameHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GameHistory
        fields = ['id', 'played_at', 'result', 'points_earned', 'duration_minutes']
        read_only_fields = ['played_at', 'id']

