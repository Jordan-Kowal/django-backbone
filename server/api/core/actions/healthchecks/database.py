"""Handler for the 'database' healthcheck"""

# Built-in
from secrets import token_urlsafe

# Django
from django.core.exceptions import FieldError, ObjectDoesNotExist

# Local
from ...models import HealthcheckDummy
from ._shared import HealthcheckHandler, Service


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class DatabaseHealthcheckHandler(HealthcheckHandler):
    """Performs an insert, update, and delete operation to test the database"""

    service = Service.DATABASE

    def main(self):
        """
        Performs an insert, update, and delete operation on our dummy model
        to check if the database is working correctly
        :raises LookupError: If we failed to create the model
        :raises ObjectDoesNotExist: If we failed to then fetch it
        :raises FieldError: If the fetched instance has invalid values
        :raises RuntimeError: If we failed to empty the table
        """
        self.content = token_urlsafe(50)
        self.instance = None
        self._create_model()
        self._fetch_model()
        self._delete_models()

    # ----------------------------------------
    # Private
    # ----------------------------------------
    def _create_model(self):
        """
        Tries to create a HealthcheckDummy instance and stores it in our state
        :raises LookupError: If we failed to create the model
        """
        self.instance = HealthcheckDummy.objects.create(content=self.content)
        if self.instance is None:
            raise LookupError("Failed to create the HealthcheckDummy instance")

    def _fetch_model(self):
        """
        Tries to fetch the recently created HealthcheckDummy instance
        :raises ObjectDoesNotExist: If we failed to fetch the instance
        :raises FieldError: If the instance does not have the right 'content' value
        """
        fetched_instance = HealthcheckDummy.objects.get(pk=self.instance.id)
        if fetched_instance is None:
            raise ObjectDoesNotExist(
                "Failed to fetch the created HealthcheckDummy instance"
            )
        if fetched_instance.content != self.content:
            raise FieldError(
                "Unexpected field value for the fetched HealthcheckDummy instance"
            )

    @staticmethod
    def _delete_models():
        """
        Tries to delete all existing HealthcheckDummy instances.
        Because the previous healthcheck might have failed before this step
        we delete all instances to avoid having remnants from previous healthchecks
        :raises RuntimeError: If there are still instances after the mass deletion
        """
        HealthcheckDummy.objects.all().delete()
        if HealthcheckDummy.objects.count() > 0:
            raise RuntimeError(
                "Failed to properly delete all HealthcheckDummy instances"
            )