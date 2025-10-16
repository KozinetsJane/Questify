from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from Questify1.settings import GPT_CHAT_API_KEY
from course.models import Lesson, Course, Quiz, Question
from course.models.quiz import Question, Quiz
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from .forms import CourseForm
from .forms import LessonForm
from .utils import generate_quiz_questions, parse_quiz_text
import requests
import os, re
from django.http import JsonResponse, Http404
from dotenv import load_dotenv
from course.models import StudentProgress, StudentAchievement, Achievement
from django.utils import timezone
from django.http import JsonResponse
import requests
import json
import logging

logger = logging.getLogger(__name__)

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

class TeacherDashboardView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    template_name = "course/teacher_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = Course.objects.filter(teacher=self.request.user)
        progress_data = StudentProgress.objects.filter(course__in=courses).select_related("student", "course")

        context["courses"] = courses
        context["progress_data"] = progress_data
        return context
    
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
def teacher_dashboard(request):
    """Панель преподавателя — просмотр прогресса всех студентов по курсам"""
    if not request.user.is_staff:
        return render(request, "403.html", status=403)

    courses = Course.objects.filter(teacher=request.user).prefetch_related("progress__student")

    context = {
        "courses": courses,
    }
    return render(request, "course/teacher_dashboard.html", context)


@login_required
def student_courses(request):
    courses = request.user.courses.all()  # или другой способ связи с курсами
    progress_records = StudentProgress.objects.filter(student=request.user).select_related("course")
    achievements = StudentAchievement.objects.filter(student=request.user).select_related("achievement")

    context = {
        "courses": courses,
        "progress_records": progress_records,
        "achievements": achievements,
    }
    return render(request, "course/student_courses.html", context)


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
            student_answers[str(question.id)] = answer
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

load_dotenv()
API_URL = os.getenv("GPT_CHAT_API_URL")
API_KEY = os.getenv("GPT_CHAT_API_KEY")


def get_hint(request, question_id):
    """
    Возвращает подсказку от AI по конкретному вопросу.
    """
    question = get_object_or_404(Question, id=question_id)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "turbo",  # как и в utils.py
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты помощник для студентов. "
                    "Дай краткую подсказку, которая направляет к правильному ответу, "
                    "но не раскрывает его напрямую."
                ),
            },
            {
                "role": "user",
                "content": f"Вопрос: {question.text}\nВарианты: A) {question.option_a}, B) {question.option_b}, C) {question.option_c}, D) {question.option_d}",
            },
        ],
        "temperature": 0.7,
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        hint = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return JsonResponse({"hint": f"Ошибка при обращении к модели: {str(e)}"})

    return JsonResponse({"hint": hint})

def update_student_progress(student, quiz, score):
    course = quiz.lesson.course
    lessons = course.lessons.all()

    completed = 0
    for lesson in lessons:
        if lesson.quiz and lesson.quiz.questions.exists():
            completed += 1

    progress, _ = StudentProgress.objects.get_or_create(student=student, course=course)
    progress.completed_lessons = completed
    progress.total_lessons = lessons.count()
    progress.score = (progress.score + score) / 2
    progress.save()

    check_achievements(student)

def check_achievements(student):
    from course.models import Achievement, StudentAchievement, StudentProgress

    progresses = StudentProgress.objects.filter(student=student)

    # 1. Первый урок
    if progresses.filter(completed_lessons__gte=1).exists():
        ach, _ = Achievement.objects.get_or_create(
            name="Первый шаг",
            defaults={"description": "Вы прошли свой первый урок!", "icon": "🌱"}
        )
        StudentAchievement.objects.get_or_create(student=student, achievement=ach)

    # 2. 100% курс
    if any(p.progress_percent() == 100 for p in progresses):
        ach, _ = Achievement.objects.get_or_create(
            name="Мастер курса",
            defaults={"description": "Вы завершили курс полностью!", "icon": "🏆"}
        )
        StudentAchievement.objects.get_or_create(student=student, achievement=ach)

    # 3. Средний балл > 90
    if any(p.score >= 90 for p in progresses):
        ach, _ = Achievement.objects.get_or_create(
            name="Отличник",
            defaults={"description": "Ваш средний балл выше 90%", "icon": "🎓"}
        )
        StudentAchievement.objects.get_or_create(student=student, achievement=ach)

def course_list(request):
    q = request.GET.get("q", "")
    sort = request.GET.get("sort", "")

    courses = Course.objects.all()

    if q:
        courses = courses.filter(title__icontains=q)

    # ⚙️ Сортировка
    if sort == "price_asc":
        courses = courses.order_by("price")
    elif sort == "price_desc":
        courses = courses.order_by("-price")
    elif sort == "level_asc":
        courses = courses.order_by("level")
    elif sort == "level_desc":
        courses = courses.order_by("-level")

    context = {"courses": courses}

    # ⚡ Возврат только части HTML, если это AJAX
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "course/course_list.html", context)

    return render(request, "course/course_list.html", context)

@csrf_exempt
def ai_assistant(request):
    logger.info("ai_assistant вызван")
    try:
        if request.method != "POST":
            logger.warning("Метод не поддерживается: %s", request.method)
            return JsonResponse({"reply": "Метод не поддерживается"}, status=405)

        # Получаем сообщение пользователя
        if request.content_type == "application/json":
            try:
                payload_data = json.loads(request.body.decode("utf-8") or "{}")
                user_message = payload_data.get("message", "").strip()
            except Exception:
                logger.exception("Неверный JSON")
                return JsonResponse({"reply": "Неверный JSON"}, status=400)
        else:
            user_message = (request.POST.get("message", "") or "").strip()

        if not user_message:
            logger.warning("Сообщение пустое")
            return JsonResponse({"reply": "Сообщение пустое"}, status=400)

        logger.info("Сообщение пользователя: %s", user_message)

        # Берём все курсы для подсказки GPT
        qs = Course.objects.select_related("teacher").prefetch_related("category").all()
        logger.info("Найдено курсов: %d", qs.count())

        # Составляем краткую инфу для GPT
        courses_brief = []
        for c in qs:
            teacher_name = getattr(c.teacher, "username", str(c.teacher))
            cats = ", ".join([cat.name for cat in c.category.all()]) or "Без категории"
            level_display = getattr(c, "get_level_display", lambda: c.level)()
            price = c.price if c.price is not None else "—"
            courses_brief.append(f"{c.title} ({level_display}, {price}$, преподаватель: {teacher_name}, категории: {cats})")

        system_prompt = (
            "Ты — AI помощник по выбору курсов.\n"
            "Вот список доступных курсов (только для справки, не выводи их все):\n"
            + "\n".join(courses_brief) +
            "\nПомоги пользователю выбрать лучший курс по его запросу. "
            "Выводи только один рекомендованный курс. "
            "В конце дай только название курса, а ссылку оставь отдельно."
        )

        url = os.getenv("GPT_CHAT_API_URL")
        key = os.getenv("GPT_CHAT_API_KEY")
        if not url or not key:
            logger.error("GPT API URL или KEY не настроены")
            return JsonResponse({"reply": "API URL или API KEY не настроены"}, status=500)

        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "model": "turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
        }

        logger.info("Отправка запроса к GPT API")
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        ai_reply = data.get("choices", [{}])[0].get("message", {}).get("content", "") or "Нет ответа от модели"
        # ❌ Удаляем строки, начинающиеся с "Ссылка: "
        ai_reply = re.sub(r"Ссылка:.*", "", ai_reply).strip()
        logger.info("AI ответ получен: %s", ai_reply)

        # Ищем курс по названию в ответе GPT
        recommended_course = None
        for c in qs:
            if c.title.lower() in ai_reply.lower():
                recommended_course = c
                break

        link = ""
        if recommended_course:
            link = request.build_absolute_uri(reverse("course:course_detail", kwargs={"pk": recommended_course.pk}))

        return JsonResponse({
            "reply": ai_reply,
            "link": link
        })

    except Exception as e:
        logger.exception("Ошибка в ai_assistant")
        return JsonResponse({"reply": f"Произошла ошибка на сервере: {e}"}, status=500)
