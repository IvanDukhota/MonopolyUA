from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('refresh/', RegisterView.as_view())
]
