from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserStat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stats')
    games = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"Статистика для {self.user.username} — Ігор: {self.games_played}, Перемог: {self.wins}, Очки: {self.points}"