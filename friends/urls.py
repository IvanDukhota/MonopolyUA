from django.urls import path
from .views import FriendList

urlpatterns = [
    path('user-friends/', FriendList.as_view()),
    path('delete-friend/', FriendList.as_view())
]