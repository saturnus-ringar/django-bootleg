from jsonview.views import JsonView

from bootleg.utils import models


class JSONSuggestView(JsonView):
    # some error handling/validation should be added here

    def dispatch(self, request, *args, **kwargs):
        self.model = models.get_editable_by_name(kwargs["model_name"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return list(self.model.objects.search_flat(self.request.GET.get("q")))
