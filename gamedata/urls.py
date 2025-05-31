from django.urls import path
from .views import AllTimePlayers

urlpatterns = [
    path('best-players/', AllTimePlayers.as_view(), name='best-players'),
]