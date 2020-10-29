
def get_default_table_class_string():
    return "table table-striped table-responsive table-hover w-100 d-block d-md-table"


def get_nav_item(url, text, count=None, target_blank=False):
    target = ''
    if target_blank:
        target = ' target="_blank" '
    html = '<li class ="nav-item">\n'
    html += '<a class="nav-link" href="%s"%s>%s\n' % (url, target, text)
    if count:
        html += '<span class ="badge badge-pill badge-danger navbar-badge">%s</span>' \
                % count
    html += '</a>\n'
    return html
