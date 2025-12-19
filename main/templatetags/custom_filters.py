from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Получить элемент из словаря по ключу"""
    if dictionary is None:
        return None
    return dictionary.get(key, [])


@register.filter
def dict_get(dictionary, key):
    """Альтернативное имя для get_item"""
    if dictionary is None:
        return None
    return dictionary.get(key, [])