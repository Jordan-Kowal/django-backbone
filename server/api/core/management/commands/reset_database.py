"""
Django command to completely reset the application database. It will:
    Remove the database
    (Optional) Remove the migration files
    (Optional) Re-create the migration files
    Apply the migrations
    (Optional) Create a super-user
Only works for sqlite3 databases
"""

# Django
from django.core.management.base import BaseCommand

# Local
from ...operations import ask_user_to_proceed, reset_sqlite3_database


# --------------------------------------------------------------------------------
# > Class
# --------------------------------------------------------------------------------
class Command(BaseCommand):
    """Django command to reset the sqlite3 database"""

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    def add_arguments(self, parser):
        """
        Handles the following command arguments:
            -a      --all       Whether to remake migration files
            -f      --force     Whether to skip the confirmation process
            -u      --user      Whether to automatically create a super user
        """
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="Whether to remake migration files",
        )
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Whether to skip the confirmation process",
        )
        parser.add_argument(
            "-u",
            "--user",
            action="store_true",
            help="Whether to automatically create a super user",
        )

    def handle(self, *args, **options):
        """Reset the sqlite3 database with various options"""
        force, remake_migrations, create_user = self._get_command_arguments(options)
        proceed = False
        if not force:
            self._show_proceed_warning(remake_migrations, create_user)
            proceed = ask_user_to_proceed()
        if force or proceed:
            reset_sqlite3_database(remake_migrations, create_user)

    # ----------------------------------------
    # Private
    # ----------------------------------------
    @staticmethod
    def _get_command_arguments(options):
        force = options.get("force", False)
        remake_migrations = options.get("all", False)
        create_user = options.get("user", False)
        return force, remake_migrations, create_user

    @staticmethod
    def _show_proceed_warning(remake_migrations, create_user):
        """
        Builds and displays the warning message for the user
        :param bool remake_migrations: Whether we will delete and remake the migration files
        :param bool create_user: Whether we will create a new super user
        """
        messages = ["The following actions will be run"]
        messages.append("  > Delete the sqlite3 database file")
        if remake_migrations:
            messages.append("  > Delete and remake the migration files")
        messages.append("  > Create a brand new sqlite3 database file")
        messages.append("  > Apply all the migrations")
        if create_user:
            messages.append("  > Create a new super user")
        warning_message = "\n".join(messages)
        print(warning_message)
