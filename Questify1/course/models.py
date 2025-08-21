from django.db import models
from django.contrib.auth.models import AbstractUser


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    
# Create your models here.
