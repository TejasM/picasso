__author__ = 'tmehta'
import re

from django import template


register = template.Library()


class StripspacesNode(template.base.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return re.sub(r'\s+', ' ', (self.nodelist.render(context).strip()))


@register.tag
def stripspaces(parser, token):
    nodelist = parser.parse(('endstripspaces',))
    parser.delete_first_token()
    return StripspacesNode(nodelist)