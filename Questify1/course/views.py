from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Course

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
# Create your views here.
