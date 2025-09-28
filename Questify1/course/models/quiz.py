from django.db import models
from . import Lesson  # импортируем Lesson из другого приложения

class Quiz(models.Model):
    lesson = models.ForeignKey("Lesson", on_delete=models.CASCADE, related_name="quizzes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"
        ordering = ['-created_at']  # сортировка по дате создания, новые сверху
    
    def __str__(self):
        return f"Тест для урока '{self.lesson.title}' ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1)

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['id']  # вопросы по порядку добавления

    def __str__(self):
        return f"{self.text[:50]}..."  # первые 50 символов текста вопроса
