from django.urls import path
from .views import AllTimePlayers, AddGameRecordView, UserGameHistoryView


urlpatterns = [
    path('best-players/', AllTimePlayers.as_view(), name='best-players'),
    path('add-game/', AddGameRecordView.as_view()),
    path('history/', UserGameHistoryView.as_view()),
]