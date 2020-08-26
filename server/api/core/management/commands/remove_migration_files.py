"""
Command that removes all the existing 'migrations' files
It technically removes all files inside "migrations" folders, except for the "__init__.py" file
"""

# Built-in
import os

# Django
from django.core.management.base import BaseCommand


# --------------------------------------------------------------------------------
# > Class
# --------------------------------------------------------------------------------
class Command(BaseCommand):
    """WIP"""

    def add_arguments(self, parser):
        """WIP"""
        pass

    def handle(self, *args, **options):
        """WIP"""
        django_directory = os.getcwd()
        print(django_directory)
