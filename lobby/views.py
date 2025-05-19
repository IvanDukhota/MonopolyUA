from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone

from .redis_client import (
    list_lobbies, get_lobby_meta,
    new_lobby_id, create_lobby, remove_lobby,
    join_lobby, leave_lobby,
    remove_player_from_lobby,
)
from .serializers import LobbyCreateSerializer, LobbyJoinSerializer

class LobbyListAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(list_lobbies())

class LobbyCreateAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LobbyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lobby_id = new_lobby_id()
        meta = {
            'id': lobby_id,
            'name': serializer.validated_data['name'],
            'region': serializer.validated_data['region'],
            'max_players': serializer.validated_data['max_players'],
            'invite_only': serializer.validated_data['invite_only'],
            'creator': str(request.user.id),
            'started': False,
            'created_at': timezone.now().isoformat()
        }
        create_lobby(meta)
        return Response(meta, status=status.HTTP_201_CREATED)

class LobbyJoinAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lobby_id):
        join_lobby(lobby_id, str(request.user.id))
        meta = get_lobby_meta(lobby_id)
        return Response(meta)

class LobbyLeaveAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lobby_id):
        leave_lobby(lobby_id, str(request.user.id))
        return Response(get_lobby_meta(lobby_id))
    
class LobbyDeleteAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lobby_id):
        meta = get_lobby_meta(str(lobby_id))
        if not meta:
            return Response({'detail': 'Lobby not found.'}, status=status.HTTP_404_NOT_FOUND)

        if str(request.user.id) != meta['creator']:
            return Response({'detail': 'You are not the creator of this lobby.'},
                            status=status.HTTP_403_FORBIDDEN)

        remove_lobby(str(lobby_id))
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class LobbyRemoveParticipantAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, lobby_id, user_id):
        meta = get_lobby_meta(str(lobby_id))
        if not meta:
            return Response({'detail': 'Lobby not found.'},
                            status=status.HTTP_404_NOT_FOUND)

        if str(request.user.id) != meta['creator']:
            return Response({'detail': 'You are not the creator of this lobby.'},
                            status=status.HTTP_403_FORBIDDEN)

        remove_player_from_lobby(str(lobby_id), str(user_id))
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    