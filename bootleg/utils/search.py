from elasticsearch_dsl import Q

from bootleg.utils.models import get_search_models


# an initial start ... to be ... improved
class QueryBuilder:

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


def get_document_by_index(index):
    for model in get_search_models():
        doc = model.get_search_document()
        if doc and doc._index._name == index:
            return doc

    return None
