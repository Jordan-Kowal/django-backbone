"""TestCase for the 'database' healthcheck"""

# Local
from ....actions.healthchecks._shared import Service
from ._shared import SERVICE_URL, HealthcheckTestCase


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestDatabaseHealthcheck(HealthcheckTestCase):
    """TestCase for the 'database' healthcheck"""

    service = Service.DATABASE
    service_base_url = f"{SERVICE_URL}/database/"
    is_meta = False
