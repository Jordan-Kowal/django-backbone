"""
Command that removes all the existing 'migrations' files of our custom apps$
Native Django models (like User) are not impacted and their migration files will remain
"""


# Django
from django.core.management.base import BaseCommand

# Local
from ...operations import ask_user_to_proceed, remove_migrations


# --------------------------------------------------------------------------------
# > Class
# --------------------------------------------------------------------------------
class Command(BaseCommand):
    """Django command to delete all our custom migration files"""

    def add_arguments(self, parser):
        """
        Handles the following command arguments:
            -f      --force     Skip the confirmation process
        """
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Allows skipping the confirmation process",
        )

    def handle(self, *args, **options):
        """Removes all the migration files of our custom apps"""
        force = options.get("force", False)
        proceed = False
        if not force:
            print("You are about to remove all of your custom apps migration files")
            proceed = ask_user_to_proceed()
        if force or proceed:
            remove_migrations()
