import os

import psutil
from django.contrib.humanize.templatetags.humanize import intword, intcomma


def humanize_int(int):
    if int >= 1000000:
        return intword(int)
    return intcomma(int)


def humanize_bytes(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_humanized_memory_usage():
    process = psutil.Process(os.getpid())
    return humanize_bytes(process.memory_info().rss)
