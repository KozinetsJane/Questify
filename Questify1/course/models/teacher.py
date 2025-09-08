from django.db import models


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
        return " ".join(filter(None, [self.surname, self.name, self.patronymic]))