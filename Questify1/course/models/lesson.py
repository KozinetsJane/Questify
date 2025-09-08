from django.db import models
from django.utils import timezone
from .course import Course

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons",verbose_name="Курс")
    title = models.CharField("Название урока", max_length=200)
    content = models.TextField("Содержание урока", blank=True, null=True)
    order = models.PositiveIntegerField("Порядковый номер урока", default=1)
    published = models.DateTimeField("Дата публикации", default=timezone.now)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}. {self.title}"


