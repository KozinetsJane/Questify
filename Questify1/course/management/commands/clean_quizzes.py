from django.core.management.base import BaseCommand
from course.models import Lesson, Quiz


class Command(BaseCommand):
    help = "Удаляет все старые тесты и оставляет только последний для каждого урока"

    def handle(self, *args, **options):
        total_deleted = 0
        lessons = Lesson.objects.all()

        for lesson in lessons:
            quizzes = Quiz.objects.filter(lesson=lesson).order_by("-created_at")
            if quizzes.count() > 1:
                # Берем id всех кроме самого нового
                to_delete_ids = quizzes.values_list("id", flat=True)[1:]
                count, _ = Quiz.objects.filter(id__in=to_delete_ids).delete()
                total_deleted += count
                self.stdout.write(
                    self.style.WARNING(
                        f"Для урока '{lesson.title}' удалено {count} старых тест(ов)"
                    )
                )

        if total_deleted == 0:
            self.stdout.write(self.style.SUCCESS("Ничего удалять не пришлось. Все уроки имеют только по одному тесту."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Готово! Удалено {total_deleted} тест(ов)."))
