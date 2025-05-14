from django.urls import path
from .views import UserProfileView, UpdateUserPictureView, UserStatView

urlpatterns = [
    path('info/', UserProfileView.as_view()),
    path('update/', UserProfileView.as_view()),
    path('avatar/', UpdateUserPictureView.as_view()),
    path('stat/', UserStatView.as_view())
]