from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Админ'),
        ('teacher', 'Преподаватель'),
        ('student', 'Студент'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def save(self, *args, **kwargs):
        if self.role == 'admin' and CustomUser.objects.filter(role='admin').exists() and not self.pk:
            raise ValueError("Может быть только один администратор")
        super().save(*args, **kwargs)
# Create your models here.
