from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Позволяет в шаблоне получить словарное значение по ключу"""
    return dictionary.get(key)

@register.filter
def split(value, sep):
    """Разделяет строку по разделителю и возвращает список"""
    return value.split(sep)


@register.filter
def get_option_text(question, letter):
    return getattr(question, f"option_{letter.lower()}", "")

@register.filter
def get_answer(student_answers, question_id):
    if not student_answers:
        return None
    return student_answers.get(str(question_id)) or student_answers.get(question_id)