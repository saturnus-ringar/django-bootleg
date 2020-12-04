from jsonview.views import JsonView

from bootleg.utils import models
from bootleg.utils.utils import get_attr__
from bootleg.views.base import StaffRequiredView


class JSONAutocompleteView(StaffRequiredView, JsonView):
    search_limit = 75
    # some error handling/validation should be added here

    def dispatch(self, request, *args, **kwargs):
        self.model = models.get_editable_by_name(kwargs["model_name"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        results = []
        query = self.request.GET.get("q")
        for result in models.search(self.model, self.model._meta.search_fields,
                                    query, autocomplete=True)[:self.search_limit]:
            for field in self.model._meta.search_fields:
                value = get_attr__(result, field)
                if query.lower() in str(value).lower():
                    if value not in results:
                        results.append(value)
        return results
