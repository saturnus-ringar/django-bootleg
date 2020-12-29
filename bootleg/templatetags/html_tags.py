from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

register = template.Library()

@register.simple_tag
def get_table_head(*args):
    html = '<table class="table table-striped table-responsive">\n'
    html += '<thead>\n'
    html += '<tr>\n'
    for arg in args:
        html += '<th>%s</th>\n' % arg

    html += '</tr>\n'
    html += '</thead>\n'
    html += '<tbody>\n'
    return mark_safe(html)


@register.simple_tag
def get_button_link(href, text):
    return mark_safe('<a href="%s"><button class="btn btn-primary">%s</button>' % (href, text))


@register.simple_tag
def get_table_end():
    html = '</tbody>\n'
    html += '</table>'
    return mark_safe(html)
