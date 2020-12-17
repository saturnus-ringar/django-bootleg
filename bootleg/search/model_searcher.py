from django.db.models import Q
from djangoql.exceptions import DjangoQLError
from djangoql.queryset import apply_search

from bootleg.utils.env import use_elastic_search
from bootleg.utils.models import SearchResults, get_order_by, filter_autocomplete_fields
from bootleg.utils.search import QueryBuilder


class ModelSearcher:

    def __init__(self, model, query=None, dql_query=None, args=None, autocomplete=False, es_limit=None):
        self.model = model
        self.es_limit = es_limit
        self.query = query
        self.dql_query = dql_query
        self.document = None
        self.args = args
        self.autocomplete = autocomplete
        self.queryset = self.model.objects.all()
        self.search_results = None

    def is_search(self):
        if self.query:
            return True
        elif self.dql_query:
            return True
        elif self.args:
            return True

        return False

    def search(self):
        self.dql_search()
        self.query_search()
        self.filter_by_args()
        self.queryset = self._get_queryset()

    def _get_queryset(self):
        prefetch_related = self.model.get_prefetch_related()
        if prefetch_related:
            self.queryset = self.queryset.prefetch_related(*prefetch_related)
        return self.queryset.order_by(*get_order_by(self.model))

    def dql_search(self):
        try:
            if self.dql_query:
                self.queryset = apply_search(self.model.objects.all(), self.dql_query)
        except DjangoQLError:
            pass

    # https://stackoverflow.com/a/1239602/9390372
    def query_search(self):
        if not self.query:
            # ugly return, indeed!
            return

        if use_elastic_search():
            self.document = self.model.get_search_document()
            if self.document:
                return self.elastic_search()

        if self.autocomplete:
            fields = filter_autocomplete_fields(self.model, self.model.get_autocomplete_fields())
        else:
            fields = self.model.get_search_field_names()

        self.queryset = self.queryset.filter(self.get_qr(fields)).distinct().order_by("id")

    def get_qr(self, fields):
        qr = None
        for field in fields:
            if not self.autocomplete:
                q = Q(**{"%s__icontains" % field: self.query})
            else:
                q = Q(**{"%s__istartswith" % field: self.query})

            if qr:
                qr = qr | q
            else:
                qr = q

        return qr

    def elastic_search(self):
        if not self.es_limit:
            raise ValueError("Can't (elastic) search without a search limit (es_limit).")
        results = self.document.search().query(QueryBuilder(self.model, self.query).get_filter())[:self.es_limit]
        self.search_results = SearchResults(results)
        self.queryset = results.to_queryset()

    def filter_by_args(self):
        if self.args:
            self.queryset = self.queryset.filter(**self.args)
