from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.management import BaseCommand
from django_elasticsearch_dsl.registries import registry

from bootleg.logging import logging
from bootleg.utils.models import lazy_bulk_fetch
from bootleg.utils.time_and_count import TimeAndCount


class Command(BaseCommand, TimeAndCount):
    logger = logging.get_logger("search_index")
    batch_size = 50

    def add_arguments(self, parser):
        parser.add_argument("-b", "--batch", default=self.batch_size, required=False)
        parser.add_argument("-p", "--parallel", action="store_true", dest="parallel")

    def handle(self, *args, **options):
        batch_size = options["batch"]
        parallel = options["parallel"]
        for doc in registry.get_documents():
            count = doc.django.model.objects.count()
            # init time and count
            self.init_tac(count, self.logger, print_every_th=1000)
            self.logger.info("Indexing model: [%s]. Batch size: [%s]. Parallel: [%s]. Total count: [%s]"
                             % (doc.django.model.__name__, batch_size, parallel, intcomma(count)))
            fetcher = lazy_bulk_fetch(batch_size, count,
                                      lambda: doc.django.model.objects.order_by("id"))
            for batch in fetcher:
                self.logger.info("Indexing: [%s]. Starting at ID: [%s]"
                                 % (doc.django.model.__name__, batch.first().id))
                doc().update(batch, parallel=parallel)
                self.update_tac(number=batch_size)
