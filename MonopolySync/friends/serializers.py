from rest_framework import serializers
from registration.models import User
from .models import Friend


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


