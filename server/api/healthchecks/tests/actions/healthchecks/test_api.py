"""TestCase for the 'api' healthcheck"""

# Local
from ....actions.healthchecks._shared import Service
from ._shared import SERVICE_URL, HealthcheckTestCase


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestApiHealthcheck(HealthcheckTestCase):
    """TestCase for the 'api' healthcheck"""

    service = Service.API
    service_base_url = f"{SERVICE_URL}/api/"
    is_meta = False
