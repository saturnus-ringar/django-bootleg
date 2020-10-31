from django.shortcuts import render

from bootleg.conf import bootleg_settings


def error_handler(request, template, status_code):
    response = render(request, template, {})
    response.status_code = status_code
    return response


def handler400(request, exception):
    return error_handler(request, bootleg_settings.TEMPLATE_404, 400)


def handler403(request, exception):
    return error_handler(request, bootleg_settings.TEMPLATE_404, 403)


def handler404(request, exception):
    return error_handler(request, bootleg_settings.TEMPLATE_404, 404)


def handler500(request):
    return error_handler(request, bootleg_settings.TEMPLATE_500, 500)
