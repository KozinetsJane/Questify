from django.contrib import admin
from .models import Course, Teacher, Category

admin.site.register(Course)
admin.site.register(Teacher)
admin.site.register(Category)

# Register your models here.
