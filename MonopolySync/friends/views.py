from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import *
from .models import Friend
from .serializers import FriendSerializer
from rest_framework.response import Response
from rest_framework import status


class FriendList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user1_friends = Friend.objects.filter(user1=user)
        user2_friends = Friend.objects.filter(user2=user)

        friends = [u.user2 for u in user1_friends] + [u.user1 for u in user2_friends]

        if not friends:
            return Response({"detail": "Друзів не знайдено."}, status=status.HTTP_404_NOT_FOUND)

        friend_serializer = FriendSerializer(friends, many=True)
        return Response(friend_serializer.data, status=HTTP_200_OK)

    def delete(self, request):
        user = request.user
        friend_id = request.data.get('friend_id')

        if not friend_id:
            return Response({"detail": "Необхідно вказати айді."}, status=status.HTTP_400_BAD_REQUEST)

        friendship1 = Friend.objects.filter(user1=user, user2_id=friend_id)
        friendship2 = Friend.objects.filter(user1_id=friend_id, user2=user)

        friendship = friendship1 | friendship2

        if friendship.exists():
            friendship.delete()
            return Response({"detail": "Друга видалено."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Друга не знайдено."}, status=status.HTTP_404_NOT_FOUND)
