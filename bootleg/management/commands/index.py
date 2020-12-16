from django.core.management import BaseCommand

from bootleg.logging import logging
from bootleg.utils.search import SearchIndexer
from bootleg.utils.time_and_count import TimeAndCount


class Command(BaseCommand, TimeAndCount):
    logger = logging.get_logger("search_index")
    batch_size = 50

    def add_arguments(self, parser):
        parser.add_argument("-b", "--batch", default=self.batch_size, required=False)
        parser.add_argument("-p", "--parallel", action="store_true", dest="parallel")

    def handle(self, *args, **options):
        SearchIndexer().run(options["batch"], options["parallel"])
