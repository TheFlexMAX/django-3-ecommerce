from django import template


register = template.Library()


@register.filter
def percentof(part, whole):
    print(part)
    print(whole)
    return int((100 * float(part) / float(whole)) * 100) / 100
