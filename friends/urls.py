from django.urls import path
from .views import FriendList

urlpatterns = [
    path('user-friends/', FriendList.as_view()),
]