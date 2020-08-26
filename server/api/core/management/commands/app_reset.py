"""
Django command to completely reset the application. It will:
    Remove the database
    Remove the migration files
    Re-create the migration files
    Apply the migrations
    Create a super-user
"""

# Django
from django.core.management.base import BaseCommand


# --------------------------------------------------------------------------------
# > Class
# --------------------------------------------------------------------------------
class Command(BaseCommand):
    """WIP"""

    pass
    # def add_arguments(self, parser):
    #     """Parses the argument from the command line"""
    #     parser.add_argument("user_id", type=int)
    #     parser.add_argument(
    #         "-f",
    #         "--force",
    #         action="store_true",
    #         help="Force record deletion even if user is not demo",
    #     )
    #
    # def handle(self, *args, **options):
    #     """Code run when the command is called"""
    #     user_id = options["user_id"]
    #     force = options.get("force", False)
    #     clear_billing_data(user_id, force)
