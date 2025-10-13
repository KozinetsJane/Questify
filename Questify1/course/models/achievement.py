from django.db import models
from django.conf import settings


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, default="🏅")
    condition = models.CharField(max_length=255, help_text="Описание условия получения")

    def __str__(self):
        return self.name


class StudentAchievement(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "achievement")

    def __str__(self):
        return f"{self.student} — {self.achievement.name}"
