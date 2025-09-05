from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField("Название категории", max_length=30, unique=True)

    def __str__(self):
            return f"{self.name}"
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        

class Teacher(models.Model):
    name = models.CharField("Имя", max_length=30)
    surname = models.CharField("Фамилия", max_length=50)
    patronymic = models.CharField("Отчество", max_length=50, null=True, blank=True)
    years_of_experience = models.PositiveIntegerField("Опыт преподавания (лет)")

    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"
        ordering = ["surname", "name"]

    def __str__(self):
        return f"{self.surname}, {self.name}, {self.patronymic}"


def course_name_validator(title: str):
    for c in title:
        if c.isalpha():
            return
        raise ValidationError("Должны быть буквы", params={'value': title}, )


class Course(models.Model):
    class LevelChoices(models.IntegerChoices): 
        BEGINNER = 1, "Начальный" 
        INTERMEDIATE = 2, "Средний" 
        ADVANCED = 3, "Продвинутый"

    title = models.CharField(max_length=200, verbose_name="Название", help_text="Название курса", validators=[course_name_validator])
    description = models.TextField(null=True, verbose_name="Описание", blank=True)
    price = models.FloatField(null=True, verbose_name="Цена", blank=True)
    published = models.DateTimeField(db_index=True, verbose_name="Опубликовано", default=timezone.now)
    level = models.SmallIntegerField("Уровень сложности", choices=LevelChoices.choices, default=LevelChoices.BEGINNER)
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=True, null=True, related_name="course")
    category = models.ManyToManyField(Category, "Категория", null=True)

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
        get_latest_by = ['-published']
    
# Create your models here.
