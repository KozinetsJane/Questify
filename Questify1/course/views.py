from django.shortcuts import render
from django.http import HttpResponse
from .models import Course


def course_list(request):
    course = Course.objects.order_by("-published")
    return render(request, 'course/course_list.html', {"course": course})

# Create your views here.
