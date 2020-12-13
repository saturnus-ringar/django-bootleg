from jsonview.views import JsonView

from bootleg.utils import models
from bootleg.utils.models import ModelSearcher
from bootleg.utils.utils import get_attr__
from bootleg.views.base import StaffRequiredView

SEARCH_LIMIT = 75


class ModelAutoCompleteView(StaffRequiredView, JsonView):

    def dispatch(self, request, *args, **kwargs):
        self.model = models.get_editable_by_name(kwargs["model_name"])
        return super().dispatch(request, *args, **kwargs)


class JSONAutocompleteView(ModelAutoCompleteView):

    def get_context_data(self, **kwargs):
        results = []
        query = self.request.GET.get("q", "")
        for result in ModelSearcher(self.model, query, autocomplete=True).get_queryset()[:SEARCH_LIMIT]:
            for field in self.model.get_autocomplete_fields():
                value = get_attr__(result, field)
                if str(value).lower().startswith(query.lower()):
                    if value and value not in results:
                        results.append(value)
        return results


class JSONFieldAutocompleteView(ModelAutoCompleteView):

    def dispatch(self, request, *args, **kwargs):
        self.field = kwargs["field_name"]
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        query = self.request.GET.get("q")
        if query:
            return list(set(self.model.objects.filter(**{"%s__istartswith" % self.field: query})
                            .values_list(self.field, flat=True).order_by("id")))
