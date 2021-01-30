"""Handler for the api healthcheck"""

# Local
from ._shared import HealthCheckHandler, Service


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class ApiHealthCheckHandler(HealthCheckHandler):
    """
    The API health check consists of making sure the API is responding.
    No specific processing is required here since we are already testing it by being here.
    """

    service = Service.API

    def main(self):
        """No need for extra actions since we are testing the API is working"""
        pass
