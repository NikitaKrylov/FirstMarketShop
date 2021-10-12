from django import template

register = template.Library()

@register.filter
def verbose_name(objects):
    return objects._meta.verbose_name_plural

@register.filter
def get_model_name(objects):
    print(object.__class__, '\n\n')
    return object.__class__._meta.model_name
