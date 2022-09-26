# coding=utf-8
from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_list_item(l, key):
    return l[key]
