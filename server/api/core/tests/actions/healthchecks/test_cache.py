"""TestCase for the 'cache' healthcheck"""

# Local
from ....actions.healthchecks._shared import Service
from ._shared import SERVICE_URL, HealthcheckTestCase


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestCacheHealthcheck(HealthcheckTestCase):
    """TestCase for the 'cache' healthcheck"""

    service = Service.CACHE
    service_base_url = f"{SERVICE_URL}/cache/"
    is_meta = False
