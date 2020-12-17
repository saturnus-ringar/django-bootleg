from jsonview.views import JsonView

from bootleg.conf import bootleg_settings
from bootleg.utils.models import ModelSearcher
from bootleg.utils.utils import get_attr__
from bootleg.views.generic_model_views import GenericModelView


class ModelAutoCompleteView(JsonView, GenericModelView):
    pass


class JSONAutocompleteView(ModelAutoCompleteView):

    def get_context_data(self, **kwargs):
        results = []
        query = self.request.GET.get("q", "")
        model_searcher = ModelSearcher(self.model, query=query, autocomplete=True,
                                       es_limit=bootleg_settings.AUTOCOMPLETE_LIMIT)
        model_searcher.search()
        # this bit could be improved ... ... .. .
        for result in model_searcher.queryset[:bootleg_settings.AUTOCOMPLETE_LIMIT]:
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
