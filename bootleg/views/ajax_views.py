from django.http import HttpResponse
from ipware import get_client_ip

from bootleg.db.models.javascript_error import JavascriptError
from bootleg.views.base import CSRFExemptView


class JavascriptErrorView(CSRFExemptView):

    def post(self, request, *args, **kwargs):
        ip, routable = get_client_ip(request)
        msg = request.POST.get("msg", None)
        url = request.POST.get("url", None)
        line = request.POST.get("line", None)
        JavascriptError.objects.create(ip, msg, url, line)
        return HttpResponse("(｡•́︿•̀｡)")
