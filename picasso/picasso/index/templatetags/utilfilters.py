__author__ = 'tmehta'

from django import template
from unidecode import unidecode as _unidecode

register = template.Library()


@register.filter('format_distance')
def format_distance_(distance):
    distance = distance.strip()
    l = []
    for t in distance.split():
        try:
            l.append(float(t))
        except ValueError:
            pass

    l = l[0]
    l = int(l / 100) / 10
    string = "{0:.2f}".format(round(l, 2))
    string += " km"
    return string


@register.filter
def unidecode(string):
    return _unidecode(string)