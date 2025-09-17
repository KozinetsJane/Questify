from django.contrib import admin
from .models import Course, Category, Teacher, Lesson


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)

# Преподаватели
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "surname", "name", "patronymic", "years_of_experience")
    search_fields = ("surname", "name", "patronymic")
    list_filter = ("years_of_experience",)
    ordering = ("surname", "name")

# Inline для уроков
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1  # показывает одну пустую форму для нового урока
    fields = ("order", "title", "content", "published")
    ordering = ("order",)
    show_change_link = True  # добавляет ссылку на редактирование отдельного урока

# Курсы
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "teacher", "price", "level", "published", "outcome")
    search_fields = ("title", "description", "teacher__surname", "teacher__name")
    list_filter = ("level", "category", "teacher")
    ordering = ("-published",)
    filter_horizontal = ("category",)
    inlines = [LessonInline]  # добавляем inline уроков

# Уроки (отдельная регистрация, если нужно отдельное редактирование)
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "order", "published")
    search_fields = ("title", "description", "content", "course__title")
    list_filter = ("course",)
    ordering = ("course", "order")
    fields = ("course", "title", "content", "order", "published")