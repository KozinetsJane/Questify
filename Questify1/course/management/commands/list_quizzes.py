from django.core.management.base import BaseCommand
from course.models import Lesson, Quiz

class Command(BaseCommand):
    help = "Показывает список уроков, для которых сгенерирован хотя бы один тест"

    def handle(self, *args, **options):
        # Используем правильный related_name
        lessons_with_quizzes = Lesson.objects.filter(quizzes__isnull=False).distinct()

        if not lessons_with_quizzes.exists():
            self.stdout.write(self.style.WARNING("Пока нет сгенерированных тестов."))
            return

        self.stdout.write(self.style.SUCCESS("Сгенерированные тесты есть для следующих уроков:"))
        for lesson in lessons_with_quizzes:
            quiz_count = Quiz.objects.filter(lesson=lesson).count()
            self.stdout.write(f"- {lesson.title} (тестов: {quiz_count})")
