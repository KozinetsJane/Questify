from django.urls import path
from .views import CourseListView, CourseDetailView, LessonDetailView, enroll_course

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('<int:course_pk>/lesson/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('<int:course_id>/enroll/', enroll_course, name='enroll_course'),
]
