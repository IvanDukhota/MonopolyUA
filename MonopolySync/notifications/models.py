from django.db import models
from registration.models import User

class Notification(models.Model):
    class Type(models.TextChoices):
        FRIEND_REQUEST = 'FRIEND', 'Friend Request'
        LOBBY_INVITE = 'LOBBY', 'Lobby Invite'
        SPAM = 'SPAM', 'Spam'

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    type = models.CharField(max_length=10, choices=Type.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(null=True, blank=True)

    lobby_id = models.IntegerField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.type})"
