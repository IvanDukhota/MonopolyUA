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

class GameHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_history')
    played_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=20)
    points_earned = models.IntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Гра користувача {self.user.username} від {self.played_at.strftime('%Y-%m-%d %H:%M')} — Результат: {self.result}, Очки: {self.points_earned}"