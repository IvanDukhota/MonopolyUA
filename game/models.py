import uuid
from django.db import models

class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    started = models.BooleanField(default=False)
    current_turn = models.IntegerField(default=0)

    def __str__(self):
        return f"Session {self.id}"


class Player(models.Model):
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name="players")
    nickname = models.CharField(max_length=50)
    position = models.IntegerField(default=0)
    money = models.IntegerField(default=1500)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.nickname} (Session {self.session.id})"
