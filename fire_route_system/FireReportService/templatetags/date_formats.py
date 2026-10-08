from django import template
from django.utils.dateparse import parse_date

register = template.Library()


@register.filter
def display_date(value):
    """Display source metadata dates using the same format as model dates."""
    if not value:
        return ''
    try:
        date = parse_date(str(value))
    except ValueError:
        date = None
    return date.strftime('%d-%m-%Y') if date else value
