from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import *
from .models import Friend
from .serializers import FriendSerializer


class FriendList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user1_friends = Friend.objects.filter(user1=user)
        user2_friends = Friend.objects.filter(user2=user)
        friends = []

        for u1 in user1_friends:
            friends.append(u1.user2)
        for u2 in user2_friends:
            friends.append(u2.user1)

        if not friends:
            return Response({"detail": "No friends found."}, status=status.HTTP_404_NOT_FOUND)

        friend_serializer = FriendSerializer(data=friends, many=True)

        return Response(friend_serializer.data, status=HTTP_200_OK)

    def delete(self, request):
        user = request.user
        friend_id = request.data.get('friend_id')

        if not friend_id:
            return Response({"detail": "Friend ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        friendship1 = Friend.objects.filter(user1=user, user2=friend_id)
        friendship2 = Friend.objects.filter(user1=friend_id, user2=user)

        friendship = friendship1 | friendship2

        if friendship.exists():
            friendship.delete()
            return Response({"detail": "Friend removed."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Friendship not found."}, status=status.HTTP_404_NOT_FOUND)