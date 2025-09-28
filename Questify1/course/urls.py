from django.urls import path
from .views import CourseListView, CourseDetailView, LessonDetailView, enroll_course
from .views import (
    TeacherCourseListView, CourseCreateView, CourseUpdateView, CourseDeleteView
)
from .views import (
    LessonCreateView, LessonDeleteView, LessonUpdateView, 
)
from .views import TeacherDashboardView
from .views import generate_quiz, enroll_course, take_quiz
from .views import StudentCourseListView


app_name = 'course'  # <- обязательно!

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('course/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('<int:course_pk>/lesson/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
    
    path('teacher/dashboard/', TeacherDashboardView.as_view(), name='teacher_dashboard'),

    # Управление курсами
    path('teacher/course/add/', CourseCreateView.as_view(), name='course_add'),
    path('teacher/course/<int:pk>/edit/', CourseUpdateView.as_view(), name='course_edit'),
    path('teacher/course/<int:pk>/delete/', CourseDeleteView.as_view(), name='course_delete'),
    path('course/<int:pk>/enroll/', enroll_course, name='enroll_course'),
    

    # Управление уроками
    path('teacher/course/<int:course_pk>/lesson/add/', LessonCreateView.as_view(), name='lesson_add'),
    path('teacher/lesson/<int:pk>/edit/', LessonUpdateView.as_view(), name='lesson_edit'),
    path('teacher/lesson/<int:pk>/delete/', LessonDeleteView.as_view(), name='lesson_delete'),

    path('lesson/<int:lesson_id>/generate_quiz/', generate_quiz, name='generate_quiz'),
    # Студент: мои курсы
    path('student/courses/', StudentCourseListView.as_view(), name='student_courses'),
    path('quiz/<int:quiz_id>/take/', take_quiz, name='take_quiz'),
]
