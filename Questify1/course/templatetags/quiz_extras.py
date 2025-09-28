from django import template

register = template.Library()

@register.filter
def get_option_text(question, letter):
    """
    Возвращает текст варианта ответа по букве.
    Предполагается, что Question хранит поля: option_a, option_b, option_c, option_d
    """
    return getattr(question, f"option_{letter.lower()}", "")

@register.filter
def get_item(dictionary, key):
    """Позволяет в шаблоне получить словарное значение по ключу"""
    return dictionary.get(key)

@register.filter
def split(value, sep):
    """Разделяет строку по разделителю и возвращает список"""
    return value.split(sep)