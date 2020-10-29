from django.utils.safestring import mark_safe


def truncate(string, max_length=100):
    if string:
        return (string[:max_length] + '..') if len(string) > max_length else string
    else:
        return None


def nl2br(string):
    string = "<br />".join(string.split("\n"))
    string = "<br />".join(string.split("\r"))
    return mark_safe(string)
