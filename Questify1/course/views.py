from django.shortcuts import render
from .models import Course
from .forms import CourseForm


def course_list(request):
    course = Course.objects.order_by("-published")
    form = CourseForm()
    return render(request, 'course/course_list.html', {"course": course, "form": form})

# Create your views here.
