from django.contrib.humanize.templatetags.humanize import intcomma
from django_elasticsearch_dsl.registries import registry

from bootleg.logging import logging
from elasticsearch_dsl import Q


from bootleg.utils.time_and_count import TimeAndCount


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


class SearchIndexer(TimeAndCount):
    logger = logging.get_logger("search_index")
    batch_size = 50

    def run(self, batch_size=None, parallel=False):
        from bootleg.utils.models import lazy_bulk_fetch
        batch_size = batch_size or self.batch_size
        parallel = parallel
        for doc in registry.get_documents():
            count = doc.django.model.objects.count()
            # init time and count
            start_id = 0 or self.get_start_id(doc)
            self.init_tac(count, self.logger, print_every_th=1000, start_count=start_id)
            self.logger.info("Indexing model: [%s]. Batch size: [%s]. Parallel: [%s]. Total count: [%s]"
                             % (doc.django.model.__name__, batch_size, parallel, intcomma(count)))
            fetcher = lazy_bulk_fetch(batch_size, count,
                                      lambda: doc.django.model.objects.order_by("id"), start=start_id)
            for batch in fetcher:
                self.logger.info("Indexing: [%s]. Starting at ID: [%s]"
                                 % (doc.django.model.__name__, batch.first().id))
                doc().update(batch, parallel=parallel)
                self.update_tac(number=batch_size)

    def get_start_id(self, doc):
        if hasattr(doc, "get_start_index_id"):
            return doc.get_start_index_id()
        return None


def get_document_by_index(index):
    # circular imports :|
    from bootleg.utils.models import get_search_models

    for model in get_search_models():
        doc = model.get_search_document()
        if doc and doc._index._name == index:
            return doc

    return None
