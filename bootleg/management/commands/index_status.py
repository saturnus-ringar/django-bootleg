from colorama import Fore
from django.core.management import BaseCommand
from django_elasticsearch_dsl.registries import registry

from bootleg.utils.printer import print_heading, print_key_value


class Command(BaseCommand):

    def handle(self, *args, **options):
        print_heading(Fore.MAGENTA + " Search index status ")
        for doc in registry.get_documents():
            print_key_value(doc.django.model.__name__ + " count", doc.django.model.objects.all().count())
            print_key_value(doc.django.model.__name__ + " documents", doc.django.model.get_search_index_total_count())
