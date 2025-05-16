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


class AllTimePlayers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        top_players = UserStat.objects.order_by('-points')[:10]
        serializer = UserStatSerializer(top_players, many=True)
        return Response({'players': serializer.data})
