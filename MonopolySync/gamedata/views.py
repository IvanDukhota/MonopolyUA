from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from .models import UserStat
from .serializers import UserStatSerializer
import requests
from django.shortcuts import redirect
from .models import GameHistory
from .serializers import GameHistorySerializer
from django.shortcuts import get_object_or_404



class AllTimePlayers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        top_players = UserStat.objects.order_by('-points')[:10]
        serializer = UserStatSerializer(top_players, many=True)
        return Response({'players': serializer.data})
class UserGameHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        games = GameHistory.objects.filter(user=user).order_by('-played_at')
        serializer = GameHistorySerializer(games, many=True)

        return Response(serializer.data,status=status.HTTP_201_CREATED)


class AddGameRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        user = get_object_or_404(User, id=user_id)

        serializer = GameHistorySerializer(data=data)
        if serializer.is_valid():
            game_record = serializer.save()
            user_stat, created = UserStat.objects.get_or_create(user=user)
            user_stat.games += 1
            if game_record.result.lower() == 'win':
                user_stat.wins += 1
            user_stat.points += game_record.points_earned
            user_stat.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)