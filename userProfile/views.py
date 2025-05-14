from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserProfileSerializer, UserProfilePictureSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print(f"User: {user}")
        print(f"Access Token from Header: {request.headers.get('Authorization')}")
        serializer = UserProfileSerializer(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        profile = request.user
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserPictureView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        profile = request.user
        serializer = UserProfilePictureSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'profile_picture': serializer.data['profile_picture']}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)