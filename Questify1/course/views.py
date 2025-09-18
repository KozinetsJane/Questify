from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from .models import Lesson, Course
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import CourseForm
from .forms import LessonForm


class CourseListView(ListView):
    model = Course
    template_name = 'course/course_list.html'
    context_object_name = 'courses'
    ordering = ['-published']
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '').strip()

        if q:
            # сопоставляем текст уровня с числом
            level_map = {
                "начальный": 1,
                "средний": 2,
                "продвинутый": 3
            }
            level_value = level_map.get(q.lower())

            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(teacher__surname__icontains=q) |
                Q(teacher__name__icontains=q) |
                Q(teacher__patronymic__icontains=q) |
                Q(category__name__icontains=q) |
                Q(level=level_value) if level_value else Q()
            ).distinct()

        return queryset


class CourseDetailView(DetailView):
    model = Course
    template_name = "course/course_detail.html"
    context_object_name = "course"


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.role == "student":  # только студент может записываться
        course.students.add(request.user)
    return redirect("course_detail", pk=course.id)
class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = "course/lesson_detail.html"
    context_object_name = "lesson"
    # LoginRequiredMixin автоматически перенаправит на страницу логина, если не авторизован.

    def dispatch(self, request, *args, **kwargs):
        # Получаем объект урока
        self.object = self.get_object()
        course = self.object.course
        user = request.user

        # Разрешаем суперадмину
        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Если в проекте у Course.teacher лежит объект User (или у Teacher есть .user),
        # поддерживаем оба варианта:
        is_teacher = False
        try:
            # если course.teacher — это уже User (AUTH_USER_MODEL)
            is_teacher = (course.teacher == user)
        except Exception:
            is_teacher = False

        # если course.teacher — объект Teacher, который имеет поле user
        if not is_teacher and hasattr(course.teacher, "user"):
            is_teacher = (course.teacher.user == user)

        if is_teacher:
            return super().dispatch(request, *args, **kwargs)

        # Разрешаем, если пользователь — студент и записан на курс
        # Предполагается, что Course имеет ManyToMany поле students (users) или related_name
        if user.is_authenticated:
            try:
                # если students — ManyToMany к модели пользователя
                if user in course.students.all():
                    return super().dispatch(request, *args, **kwargs)
            except Exception:
                # если students нет или структура другая — отказываем
                pass

        # Иначе — доступ запрещён
        return HttpResponseForbidden("У вас нет доступа к этому уроку.")
    

# Проверка, что пользователь — преподаватель
class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'teacher'

class TeacherDashboardView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "course/teacher_dashboard.html"  # корректно, т.к. в course/templates/
    context_object_name = "courses"

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)
    
# Список курсов преподавателя
class TeacherCourseListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Course
    template_name = "course/teacher_dashboard.html"
    context_object_name = "courses"

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)

# Создание нового курса
class CourseCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "course/course_form.html"

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('teacher_dashboard')

# Редактирование курса
class CourseUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "course/course_form.html"

    def get_queryset(self):
        # чтобы преподаватель мог редактировать только свои курсы
        return Course.objects.filter(teacher=self.request.user)

    def get_success_url(self):
        return reverse_lazy('teacher_dashboard')

# Удаление курса
class CourseDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Course
    template_name = "course/course_confirm_delete.html"

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)

    def get_success_url(self):
        return reverse_lazy('teacher_dashboard')
    
class LessonCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = "course/lesson_form.html"

    def form_valid(self, form):
        course_id = self.kwargs.get('course_pk')
        form.instance.course_id = course_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('teacher_dashboard')

# Редактирование урока
class LessonUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = "course/lesson_form.html"

    def get_queryset(self):
        # можно редактировать только уроки своих курсов
        return Lesson.objects.filter(course__teacher=self.request.user)

    def get_success_url(self):
        return reverse_lazy('teacher_dashboard')

# Удаление урока
class LessonDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Lesson
    template_name = "course/lesson_confirm_delete.html"

    def get_queryset(self):
        return Lesson.objects.filter(course__teacher=self.request.user)

    def get_success_url(self):
        return reverse_lazy('teacher_dashboard')


# Create your views here.
