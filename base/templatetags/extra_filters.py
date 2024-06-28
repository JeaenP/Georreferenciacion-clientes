from django import template
import calendar

register = template.Library()

@register.filter
def to_months(value):
    return range(1, 13)

@register.filter
def month_name(month_number):
    return calendar.month_name[month_number]