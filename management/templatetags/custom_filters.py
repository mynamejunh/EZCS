from django import template

register = template.Library()

@register.filter
def split(value, key):
    return value.split(key)

@register.filter
def index(value, index):
    try:
        return value[index]
    except (IndexError, TypeError):
        return None
    
@register.filter(name='basename')
def basename(value):
    import os
    return os.path.basename(value)