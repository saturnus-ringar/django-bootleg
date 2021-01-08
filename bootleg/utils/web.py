from django.http import HttpResponseRedirect
from django.urls import reverse


def get_error_redirect(error):
    return HttpResponseRedirect(reverse("bootleg:general_error") + "?message=%s" % error)
