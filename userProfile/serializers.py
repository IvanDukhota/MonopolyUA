from rest_framework import serializers
from django.conf import settings
from registration.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture',  'region', 'game_currency']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(
                obj.profile_picture.url) if request else f"{settings.MEDIA_URL}{obj.profile_picture.url}"
        return None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'region', 'game_currency']


class UserProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_picture']