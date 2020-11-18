import os

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Prints all environment variables"

    def handle(self, *args, **options):
        for item, value in sorted(os.environ.items()):
            self.stdout.write('{}: {}'.format(item, value))
