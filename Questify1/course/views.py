from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from course.models import Lesson, Course, Quiz, Question
from course.models.quiz import Question, Quiz

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import CourseForm
from .forms import LessonForm
from .utils import generate_quiz_questions, parse_quiz_text




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

class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "course/student_courses.html"  # создайте этот шаблон
    context_object_name = "courses"

    def get_queryset(self):
        # возвращаем только курсы, на которые подписан текущий студент
        user = self.request.user
        return Course.objects.filter(students=user)
       
# Создание нового курса
class CourseCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "course/course_form.html"

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('course:teacher_dashboard')

# Редактирование курса
class CourseUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "course/course_form.html"

    def get_queryset(self):
        # чтобы преподаватель мог редактировать только свои курсы
        return Course.objects.filter(teacher=self.request.user)

    def get_success_url(self):
        return reverse_lazy('course:teacher_dashboard')

# Удаление курса
class CourseDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Course
    template_name = "course/course_confirm_delete.html"

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)

    def get_success_url(self):
        return reverse_lazy('course:teacher_dashboard')
    
class LessonCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = "course/lesson_form.html"

    def form_valid(self, form):
        course_id = self.kwargs.get('course_pk')
        form.instance.course_id = course_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('course:teacher_dashboard')

# Редактирование урока
class LessonUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = "course/lesson_form.html"

    def get_queryset(self):
        # можно редактировать только уроки своих курсов
        return Lesson.objects.filter(course__teacher=self.request.user)

    def get_success_url(self):
        return reverse_lazy('course:teacher_dashboard')

# Удаление урока
class LessonDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Lesson
    template_name = "course/lesson_confirm_delete.html"

    def get_queryset(self):
        return Lesson.objects.filter(course__teacher=self.request.user)

    def get_success_url(self):
        return reverse_lazy('course:teacher_dashboard')

@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.students.add(request.user)
    course.save()
    return redirect('course:course_detail', pk=course.pk) 

def lesson_quiz_view(request, lesson_id):
    """
    Отображает тест для урока (без проверки прав пользователя).
    Использует утилиты для генерации вопросов.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)

    raw_text = generate_quiz_questions(lesson.content)
    quiz = parse_quiz_text(raw_text) if not raw_text.startswith("Ошибка") else []

    return render(request, "course/lesson_quiz.html", {
        "lesson": lesson,
        "quiz": quiz,
        "error": None if quiz else raw_text,  # если пусто — покажем текст ошибки
    })


@login_required
def generate_quiz(request, lesson_id):
    """
    Генерация теста для урока с проверкой, что текущий пользователь — преподаватель.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Проверка прав
    if request.user != lesson.course.teacher:
        return render(request, "course/error.html", {
            "message": "У вас нет прав для генерации теста."
        })

    # Генерация вопросов через GPT-чат
    raw_text = generate_quiz_questions(lesson.content)
    if not raw_text or raw_text.startswith("Ошибка"):
        return render(request, "course/quiz_generated.html", {
            "lesson": lesson,
            "quiz_text": [],
            "error": raw_text or "Пустой ответ от модели."
        })
    # Парсим текст в список вопросов
    questions = parse_quiz_text(raw_text)

    # Сохраняем Quiz и вопросы в базу
    quiz = Quiz.objects.create(lesson=lesson)
    for q in questions:
        Question.objects.create(
            quiz=quiz,
            text=q["question"],
            option_a=q["options"][0] if len(q["options"]) > 0 else "",
            option_b=q["options"][1] if len(q["options"]) > 1 else "",
            option_c=q["options"][2] if len(q["options"]) > 2 else "",
            option_d=q["options"][3] if len(q["options"]) > 3 else "",
            correct_answer=q["answer"] or ""
        )

    return render(request, "course/quiz_generated.html", {
        "lesson": lesson,
        "quiz_text": questions,
        "error": None
    })

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()  # related_name="questions" в Question

    if request.method == "POST":
        total = questions.count()
        score = 0
        student_answers = {}

        for question in questions:
            answer = request.POST.get(f"question_{question.id}")
            student_answers[question.id] = answer
            if answer == question.correct_answer:
                score += 1

        context = {
            "quiz": quiz,
            "questions": questions,
            "student_answers": student_answers,
            "score": score,
            "total": total,
            "completed": True
        }
        return render(request, "course/take_quiz.html", context)

    else:
        # GET-запрос, просто показываем вопросы
        context = {
            "quiz": quiz,
            "questions": questions,
            "completed": False
        }
        return render(request, "course/take_quiz.html", context)