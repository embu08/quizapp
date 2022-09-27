# coding=utf-8
from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_list_item(l, key):
    return l[key]


@register.filter
def divide(value, arg):
    try:
        return round(int(value) / int(arg) * 100, 2)
    except (ValueError, ZeroDivisionError):
        return None
