from django.shortcuts import render
from django.http import HttpResponse

def course_list(request):
    return HttpResponse("Здесь будет выведен список курсов.")

# Create your views here.
