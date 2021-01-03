import uuid

from django.db.models import Q
from djangoql.exceptions import DjangoQLError
from djangoql.queryset import apply_search
from django.conf import settings
from bootleg.utils.env import use_elastic_search, is_postgres
from bootleg.utils.models import SearchResults, get_order_by, filter_autocomplete_fields


if is_postgres():
    # to...fix
    pass


class QueryBuilder:
    # an initial start ... to be ... improved

    def __init__(self, model, query):
        self.model = model
        self.query = query

    def get_filter(self):
        filter = None
        for field in self.model.get_search_document_field_names():
            f = Q("match", **{"%s" % field: self.query})
            if filter:
                filter = filter | f
            else:
                filter = f

        return filter

    def __init__(self, model, query):
        self.model = model
        self.query = query

    def get_filter(self):
        filter = None
        for field in self.model.get_search_document_field_names():
            f = Q("match", **{"%s" % field: self.query})
            if filter:
                filter = filter | f
            else:
                filter = f

        return filter


class ModelSearcher:

    def __init__(self, model, query=None, dql_query=None, args=None, autocomplete=False, es_limit=None, force_es=False,
                 forced_query=None):
        self.model = model
        self.force_es = force_es
        self.es_limit = es_limit
        self.query = query
        self.forced_query = forced_query
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
        self.cleanup_queries()
        self.dql_search()
        self.query_search()
        self.filter_by_args()
        return self

    def cleanup_queries(self):
        non_allowed_strings = getattr(settings, "NON_ALLOWED_QUERY_STRINGS", None)
        for non_allowed_string in non_allowed_strings:
            print(self.dql_query)
            # set the queries to something that will never be found: uuid.uuid4()
            if self.query and non_allowed_string.lower() in self.query.lower():
                self.query = str(uuid.uuid4())
            elif self.dql_query and non_allowed_string.lower() in self.dql_query:
                self.dql_query = self.dql_query.lower().replace(non_allowed_string.lower(), str(uuid.uuid4()))
            elif self.forced_query and non_allowed_string.lower in self.forced_query:
                self.forced_query = str(uuid.uuid4())

        print("self.query: %s" % self.query)
        print("self.dql_query: %s" % self.dql_query)
        print("self.forced_query: %s" % self.forced_query)


    def get_queryset(self):
        prefetch_related = self.model.get_prefetch_related()
        if prefetch_related:
            self.queryset = self.queryset.prefetch_related(*prefetch_related)
        return self.queryset.order_by(*get_order_by(self.model))

    def dql_search(self):
        try:
            if self.dql_query:
                self.queryset = apply_search(self.model.objects.all(), self.dql_query)
        except DjangoQLError as e:
            pass

    # https://stackoverflow.com/a/1239602/9390372
    def query_search(self):
        if not self.query and not self.forced_query:
            # ugly return, indeed!
            return

        if self.force_es or use_elastic_search():
            self.document = self.model.get_search_document()
            if self.document:
                return self.elastic_search()

        if not self.autocomplete and self.model.get_exact_match_field_names() and not self.forced_query:
            # searching by exact matches only
            self.queryset = self.queryset.filter(self.get_qr_exact(self.model.get_exact_match_field_names())).distinct()\
                .order_by("id")
        else:
            if self.autocomplete:
                fields = filter_autocomplete_fields(self.model, self.model.get_autocomplete_fields())
            else:
                fields = self.model.get_search_field_names()

            self.queryset = self.queryset.filter(self.get_qr(fields)).distinct().order_by("id")

    def get_qr_exact(self, fields):
        qr = None
        for field in fields:
            q = Q(**{"%s" % field: self.query})
            if qr:
                qr = qr | q
            else:
                qr = q
        return qr

    def get_qr(self, fields):
        query = self.query
        if self.forced_query:
            query = self.forced_query
        qr = None
        for field in fields:
            if not self.autocomplete:
                q = Q(**{"%s__icontains" % field: query})
            else:
                q = Q(**{"%s__istartswith" % field: query})

            if qr:
                qr = qr | q
            else:
                qr = q

        return qr

    def elastic_search(self):
        if not self.es_limit:
            raise ValueError("Can't (elastic) search without a search limit (es_limit).")
        get_filter_method = getattr(self.document, "get_filter")
        if get_filter_method:
            filter = get_filter_method(self.query)
        else:
            filter = QueryBuilder(self.model, self.query)
        results = self.document.search().query(filter)[:self.es_limit]
        self.search_results = SearchResults(results)

    def filter_by_args(self):
        if self.args:
            self.queryset = self.queryset.filter(**self.args)
