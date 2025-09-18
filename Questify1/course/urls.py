from django.urls import path
from .views import CourseListView, CourseDetailView, LessonDetailView, enroll_course
from .views import (
    TeacherCourseListView, CourseCreateView, CourseUpdateView, CourseDeleteView
)
from .views import (
    LessonCreateView, LessonDeleteView, LessonUpdateView, 
)
from .views import TeacherDashboardView

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('<int:course_pk>/lesson/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('<int:course_id>/enroll/', enroll_course, name='enroll_course'),

    # Панель преподавателя
    path('teacher/dashboard/', TeacherDashboardView.as_view(), name='teacher_dashboard'),

    # Управление курсами
    path('teacher/course/add/', CourseCreateView.as_view(), name='course_add'),
    path('teacher/course/<int:pk>/edit/', CourseUpdateView.as_view(), name='course_edit'),
    path('teacher/course/<int:pk>/delete/', CourseDeleteView.as_view(), name='course_delete'),

    # Управление уроками
    path('teacher/course/<int:course_pk>/lesson/add/', LessonCreateView.as_view(), name='lesson_add'),
    path('teacher/lesson/<int:pk>/edit/', LessonUpdateView.as_view(), name='lesson_edit'),
    path('teacher/lesson/<int:pk>/delete/', LessonDeleteView.as_view(), name='lesson_delete'),
]
