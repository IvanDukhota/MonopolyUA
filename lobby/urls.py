from django.urls import path
from .views import (
    LobbyListAPI, LobbyCreateAPI, LobbyJoinAPI, LobbyLeaveAPI, LobbyDeleteAPI, LobbyRemoveParticipantAPI, LobbyStartAPI
)

urlpatterns = [
    path('', LobbyListAPI.as_view(), name='lobby-list'),
    path('create/', LobbyCreateAPI.as_view(), name='lobby-create'),
    path('<uuid:lobby_id>/join/', LobbyJoinAPI.as_view(), name='lobby-join'),
    path('<uuid:lobby_id>/leave/', LobbyLeaveAPI.as_view(), name='lobby-leave'),
    path('<uuid:lobby_id>/delete/', LobbyDeleteAPI.as_view(), name='lobby-delete'),
    path('<uuid:lobby_id>/remove/<int:user_id>/', LobbyRemoveParticipantAPI.as_view(), name='lobby-remove-participant'),
    path('<uuid:lobby_id>/start/', LobbyStartAPI.as_view(), name='lobby-start'),
]