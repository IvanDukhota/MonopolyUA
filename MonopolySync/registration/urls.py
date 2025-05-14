from django.urls import path
from .views import RegisterView, LoginView, GoogleLoginRedirectView, GoogleCallbackView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('google/login/', GoogleLoginRedirectView.as_view(), name='google-auth'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google-auth'),

]
