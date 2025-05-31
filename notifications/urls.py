from django.urls import path
from .views import NotificationsView, ManageNotifications

urlpatterns = [
    path('', NotificationsView.as_view()),
    path('manage/<int:notification_id>/', ManageNotifications.as_view()),
]