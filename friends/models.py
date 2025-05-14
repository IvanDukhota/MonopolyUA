from django.db import models
from registration.models import User


class Friend(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_user2')
    date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user1', 'user2']

    def __str__(self):
        return f"{self.user1} and {self.user2} on date {self.date}"


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_from')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_to')
    date = models.DateTimeField(auto_now=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Request from {self.from_user} to {self.to_user} status {self.is_accepted}"
