from rest_framework import serializers

class LobbyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    region = serializers.CharField(max_length=50)
    max_players = serializers.ChoiceField(choices=[2, 3, 4])
    invite_only = serializers.BooleanField(default=False)

class LobbyJoinSerializer(serializers.Serializer):
    # для join/leave достаточно user из request
    pass