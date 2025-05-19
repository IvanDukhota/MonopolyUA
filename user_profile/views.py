from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserProfileSerializer, UserProfilePictureSerializer, UserStatSerializer
from gamedata.models import UserStat

from users.models import User

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        profile = request.user
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetailAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UpdateUserPictureView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        profile = request.user
        serializer = UserProfilePictureSerializer(profile, data=request.data, partial=True,
                                                  context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response({'avatar': serializer.data['avatar']}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserStatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            user_stat = UserStat.objects.get(user=user)
            lose = user_stat.games - user_stat.wins
            percentage = user_stat.wins / user_stat.games * 100 if user_stat.games > 0 else 0
        except UserStat.DoesNotExist:
            return Response({"detail": "Статистика не знайдена."}, status=404)

        serializer = UserStatSerializer(user_stat)
        data = serializer.data
        data["lose"] = lose
        data["percentage"] = round(percentage, 2)

        return Response(data)

