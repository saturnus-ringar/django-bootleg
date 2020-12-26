import time

from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.management import BaseCommand

from bootleg.search.model_searcher import ModelSearcher
from bootleg.utils import env
from bootleg.utils.search import get_document_by_index, QueryBuilder


class Command(BaseCommand):
    limit = 25

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("-i", "--index", required=True)
        parser.add_argument("-f", "--field", required=False)
        parser.add_argument("-qs", "--queryset", action="store_true", default=False)
        parser.add_argument("-q", "--query", required=True)
        parser.add_argument("-l", "--limit", default=self.limit, type=int, required=False)

    def handle(self, *args, **options):
        index = options["index"]
        query = options["query"]
        limit = options["limit"]
        field = options["field"]
        self.search_result_time = 0
        self.query_fetch_time = 0
        self.search_documents(index, query, limit, field)
        if options["queryset"]:
            self.search_models()

    def search_documents(self, index, query, limit, field):
        document = get_document_by_index(index)
        print("Searching index: [%s] using query: [%s]. Total count: [%s]"
              % (index, query, intcomma(document.django.model.get_search_index_total_count())))
        print("Using filter: [%s]" % filter)
        start_time = time.time()
        model_searcher = ModelSearcher(document.django.model, query, es_limit=limit, force_es=True).search()
        print("**** Document results ********************")
        for res in model_searcher.search_results:
            if field and getattr(res, field, None):
                print(getattr(res, field, None))
                print("------------------------------------------------------------------------------ ")
            else:
                print(res)

        self.search_result_time = time.time() - start_time
        self.get_queryset(model_searcher.search_results)
        self.finalize()

    def get_queryset(self, results):
        print("**** Document results ********************")
        start_time = time.time()
        for o in results.to_queryset():
            print("Found result: [%s]" % o)
        if results.count() == 0:
            print("No results found.")

        self.query_fetch_time = time.time() - start_time

    def finalize(self):
        self.stdout.write("It took: [%s] seconds search the documents." % round(self.search_result_time, 3))
        self.stdout.write("It took: [%s] seconds to fetch they queryset." % round(self.query_fetch_time, 3))

