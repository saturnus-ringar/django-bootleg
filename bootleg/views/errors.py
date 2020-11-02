from django.shortcuts import render

from bootleg.conf import bootleg_settings


def error_handler(request, template, status_code):
    response = render(request, template, {})
    response.status_code = status_code
    return response


def handler400(request, exception):
    return error_handler(request, bootleg_settings.ERROR_400_TEMPLATE, 400)


def handler403(request, exception):
    return error_handler(request, bootleg_settings.ERROR_403_TEMPLATE, 403)


def handler404(request, exception):
    return error_handler(request, bootleg_settings.ERROR_404_TEMPLATE, 404)


def handler500(request):
    return error_handler(request, bootleg_settings.ERROR_500_TEMPLATE, 500)
