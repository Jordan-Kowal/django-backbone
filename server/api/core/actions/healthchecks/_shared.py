"""Shared utility classes, functions, and constants for the Healthcheck actions"""

# Built-in
import logging
from enum import Enum

# Django
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

# Personal
from jklib.django.drf.actions import ActionHandler, SerializerMode

# --------------------------------------------------------------------------------
# > Constants
# --------------------------------------------------------------------------------
LOGGER = logging.getLogger("healthcheck")


class Service(Enum):
    """List of services with healthchecks"""

    API = "API"
    CACHE = "CACHE"
    DATABASE = "DATABASE"
    MIGRATIONS = "MIGRATIONS"


# --------------------------------------------------------------------------------
# > Actions
# --------------------------------------------------------------------------------
class HealthcheckHandler(ActionHandler):
    """
    Extends the ActionHandler to add logs after the healthcheck
    Any action inheriting from this class should:
        Set their 'service' attribute correctly
        Their .main() method does not need to return anything
        Their .main() must perform action that would crash IF the service was unhealthy
    If the service crashes, THIS class will intercept it and return a failed healthcheck
    """

    serializer_mode = SerializerMode.NONE
    serializer = None
    service = None

    def run(self):
        """
        Overridden to log the results before returning the response
        :raises AttributeError: If the 'service' attribute is not correctly defined
        :return: Response instance from DRF, containing our results
        :rtype: Response
        """
        # Cannot proceed is service is not set
        if not self.has_service():
            raise AttributeError(
                f"Class {self.__name__} is missing a valid 'service' attribute"
            )
        action_to_run = getattr(self, self.method, self.main)
        code = HTTP_500_INTERNAL_SERVER_ERROR  # Changes only if success
        try:
            action_to_run()
        except Exception as error:
            LOGGER.error(f"Service {self.service} is KO: {error}")
        else:
            code = HTTP_200_OK
            LOGGER.info(f"Service {self.service} is OK")
        finally:
            return Response(None, status=code)

    def has_service(self):
        """
        :return: Whether the 'service' attribute is valid
        :rtype: bool
        """
        return self.service in Service
