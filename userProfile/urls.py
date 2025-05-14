from django.urls import path
from .views import UserProfileView, UpdateUserProfileView, UserProfileView

urlpatterns = [
    path('info/', UserProfileView.as_view()),
    path('update/', UpdateUserProfileView.as_view())
]