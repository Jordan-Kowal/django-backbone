"""
Command that initialize a Django application.
It simply make and apply migrations, and create a super user
"""


# Personal
from jklib.django.commands.commands import ImprovedCommand

# Local
from ...operations import OperationInitDjango


# --------------------------------------------------------------------------------
# > Class
# --------------------------------------------------------------------------------
class Command(ImprovedCommand):
    """Command to initialize a Django app from scratch"""

    operation_class = OperationInitDjango

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
        """Triggers an operation to initialize a Django App"""
        force = options.get("force", False)
        proceed = False
        if not force:
            print("You are about to apply database migrations and create a superuser.")
            proceed = self.ask_user_to_proceed()
        if force or proceed:
            self.run_operation()
