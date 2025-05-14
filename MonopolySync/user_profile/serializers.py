from rest_framework import serializers
from django.conf import settings
from registration.models import User
from gamedata.models import UserStat


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'avatar',  'region', 'game_currency']

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(
                obj.avatar.url) if request else f"{settings.MEDIA_URL}{obj.avatar.url}"
        return None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'region', 'game_currency']


class UserProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['avatar']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if instance.avatar:
            avatar_url = instance.avatar.url
            if request:
                full_url = request.build_absolute_uri(avatar_url)
            else:
                full_url = f"http://localhost:8000{avatar_url}"
            representation['avatar'] = full_url
        else:
            representation['avatar'] = None

        return representation


class UserStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStat
        fields = '__all__'