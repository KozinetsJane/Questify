from django.db import models
from django.utils import timezone
from users.models import CustomUser
from django.conf import settings



class Category(models.Model):
    name = models.CharField("Название категории", max_length=30, unique=True)

    def __str__(self):
            return f"{self.name}"
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Course(models.Model):
    class LevelChoices(models.IntegerChoices): 
        BEGINNER = 1, "Начальный" 
        INTERMEDIATE = 2, "Средний" 
        ADVANCED = 3, "Продвинутый"

    title = models.CharField(max_length=200, verbose_name="Название", help_text="Название курса")
    description = models.TextField(null=True, verbose_name="Описание", blank=True)
    price = models.FloatField(null=True, verbose_name="Цена", blank=True)
    published = models.DateTimeField(db_index=True, verbose_name="Опубликовано", default=timezone.now)
    level = models.SmallIntegerField("Уровень сложности", choices=LevelChoices.choices, default=LevelChoices.BEGINNER)
    outcome = models.TextField(blank=True, null=True, help_text="Что студент сможет после прохождения курса")
    image = models.ImageField(upload_to="course_images/", blank=True, null=True)
    
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, default=1)
    category = models.ManyToManyField(Category, verbose_name="Категория", blank=True)
    students = models.ManyToManyField(CustomUser, related_name="enrolled_courses", blank=True)

    def __str__(self):
        return f"{self.title} {self.price}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print("Данные сохранены")
    
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        print("Данные удалены")

    @property
    def same_teacher_course(self):
        return Course.objects.filter(teacher=self.teacher).exclude(pk=self.pk)


    class Meta:
        verbose_name_plural = "Курсы"
        verbose_name = "Курс"
        ordering = ['-published']
        unique_together = ["title", "teacher"]
        get_latest_by = "published"
    
# Create your models here.
