from django.shortcuts import render

from bootleg.conf import bootleg_settings
from bootleg.logging import logging


def error_handler(request, template, status_code):
    response = render(request, template, {})
    response.status_code = status_code
    return response


def log(status_code, request):
    logging.get_logger("bootleg.errors/%s" % str(status_code)).error("%s on the URL: %s" %
                                                             (str(status_code), request.get_full_path()))


def handler400(request, exception):
    log(400, request)
    return error_handler(request, bootleg_settings.ERROR_400_TEMPLATE, 400)


def handler403(request, exception):
    log(403, request)
    return error_handler(request, bootleg_settings.ERROR_403_TEMPLATE, 403)


def handler404(request, exception):
    log(404, request)
    return error_handler(request, bootleg_settings.ERROR_404_TEMPLATE, 404)


def handler500(request):
    return error_handler(request, bootleg_settings.ERROR_500_TEMPLATE, 500)
