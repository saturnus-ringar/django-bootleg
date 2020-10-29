from django.shortcuts import render

from bootleg.conf import settings


def error_handler(request, template, status_code):
    response = render(request, template, {})
    response.status_code = status_code
    return response


def handler400(request, exception):
    return error_handler(request, settings.template_400(), 400)


def handler403(request, exception):
    return error_handler(request, settings.template_403(), 403)


def handler404(request, exception):
    return error_handler(request, settings.emplate_404(), 404)


def handler500(request):
    return error_handler(request, settings.template_500(), 500)
