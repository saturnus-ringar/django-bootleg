from django.core.management import BaseCommand
from elasticsearch_dsl import Q

from bootleg.utils.search import get_document_by_index, QueryBuilder


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("-i", "--index", required=True)
        parser.add_argument("-q", "--query", required=True)
        parser.add_argument("-l", "--limit", type=int, required=False)

    def handle(self, *args, **options):
        query = options["query"]
        index = options["index"]
        limit = options["limit"] or 15
        document = get_document_by_index(options["index"])
        if not document:
            raise ValueError("Could not find any document from the index: [%s]" % options["index"])

        self.stdout.write("Searching index: [%s] using query: [%s]" % (index, query))
        filter = QueryBuilder(document.Django.model, query).get_filter()
        self.stdout.write("Using filter: [%s]" % filter)
        results = document.search().query("bool", filter=QueryBuilder(document.Django.model, query).get_filter())[:limit]

        for o in results.to_queryset():
            self.stdout.write("Found result: [%s]" % o)

        if results.count() == 0:
            self.stdout.write("No results found.")
