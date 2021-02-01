"""TestCase for the 'migrations' healthcheck"""

# Local
from ....actions.healthchecks._shared import Service
from ._shared import SERVICE_URL, HealthcheckTestCase


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class TestMigrationsHealthcheck(HealthcheckTestCase):
    """TestCase for the 'migrations' healthcheck"""

    service = Service.MIGRATIONS
    service_base_url = f"{SERVICE_URL}/migrations/"
    is_meta = False
