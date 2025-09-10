from django.shortcuts import render
from django.views.generic import ListView
from .models import Course
from .forms import CourseForm


class CourseListView(ListView):
    model = Course
    template_name = 'course/course_list.html'
    context_object_name = 'courses'
    ordering = ['-published']
    paginate_by = 10
    

def course_list(request):
    course = Course.objects.order_by("-published")
    form = CourseForm()
    return render(request, 'course/course_list.html', {"course": course, "form": form})

# Create your views here.
