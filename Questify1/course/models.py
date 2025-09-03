from django.db import models
from django.utils import timezone


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(null=True, verbose_name="Описание", blank=True)
    price = models.FloatField(null=True, verbose_name="Цена", blank=True)
    published = models.DateTimeField(db_index=True, verbose_name="Опубликовано", default=timezone.now)

    def __str__(self):
        return f"{self.title} {self.price}"

    class Meta:
        verbose_name_plural = "Курсы"
        verbose_name = "Курс"
        ordering = ['-published']
    
# Create your models here.
