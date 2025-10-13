from django.db import models
from django.conf import settings


class StudentProgress(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE, related_name='progress')
    completed_lessons = models.IntegerField(default=0)
    total_lessons = models.IntegerField(default=0)
    score = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')
        verbose_name = "Прогресс студента"
        verbose_name_plural = "Прогрессы студентов"

    def progress_percent(self):
        if self.total_lessons == 0:
            return 0
        return round((self.completed_lessons / self.total_lessons) * 100, 1)

    def __str__(self):
        return f"{self.student} — {self.course}: {self.progress_percent()}%"
