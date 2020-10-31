from re import compile
from django.http import HttpResponseRedirect
from django.utils.http import urlencode

from bootleg.middleware.base import BaseMiddleware
from django.urls import reverse
from bootleg.conf import bootleg_settings


EXEMPT_URLS = [
    compile(str(reverse("bootleg:change_password") + '.*')),
    compile(str(reverse("bootleg:login"))),
]

# add custom exempt URLs from a function, if it exists
exempt_urls_function = bootleg_settings.LOGIN_EXEMPT_URLS_FUNCTION

if exempt_urls_function:
    for url in exempt_urls_function():
        EXEMPT_URLS.append(compile(url))


class LoginMiddleware(BaseMiddleware):

    def process_request(self, request):
        path = request.path_info
        # redirect logged in users at the login page to the home url
        if path == reverse("bootleg:login") and request.user.is_authenticated:
            return HttpResponseRedirect(bootleg_settings.home_url())

        if not request.user.is_authenticated:
            if not any(m.match(path) for m in EXEMPT_URLS):
                if request.get_full_path() != "/":
                    return HttpResponseRedirect(reverse("bootleg:login") + "?" + urlencode({"next": request.get_full_path()}))
                else:
                    return HttpResponseRedirect(reverse("bootleg:login"))
