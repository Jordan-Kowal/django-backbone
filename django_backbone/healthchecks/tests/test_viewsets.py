"""Tests for the 'healthchecks' viewsets"""

# Personal
from jklib.django.utils.tests import assert_logs

# Application
from core.tests import BaseActionTestCase
from users.factories import AdminFactory

# Local
from ..viewsets import Service

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
SERVICE_URL = "/api/admin/healthchecks/"


class BaseTestCase(BaseActionTestCase):
    """Base class for healthcheck tests that provides utilities"""

    # Constant
    url_template = f"{SERVICE_URL}/{{service}}/"
    http_method_name = "GET"
    success_code = 200

    # To override
    service = None

    def setUp(self):
        """Creates and logs an admin, then stores the service endpoint"""
        self.admin = AdminFactory()
        self.api_client.force_authenticate(self.admin)
        self.endpoint_url = self.url(context={"service": self.service.name.lower()})

    @property
    def error_message(self):
        """
        :return: The START of the error message logged in the logfile
        :rtype: str
        """
        return f"ERROR:healthcheck:Service {self.service.name} is KO"

    @property
    def success_message(self):
        """
        :return: The COMPLETE success message logged in the logfile
        :rtype: str
        """
        return f"INFO:healthcheck:Service {self.service.name} is OK"


class SharedMixin:
    """Group of tests that works with BaseTestClass"""

    @assert_logs(logger="healthcheck", level="INFO")
    def test_permissions(self):
        """Tests that only an admin can access this service"""
        self.assert_admin_permissions(self.endpoint_url)

    def test_healthcheck_failure(self):
        """Cannot be tested"""
        pass

    @assert_logs(logger="healthcheck", level="INFO")
    def test_healthcheck_success(self):
        """Tests the service is working and the call appears in the logfile"""
        response = self.http_method(self.endpoint_url)
        assert response.status_code == self.success_code
        assert self.success_message == self.logger_context.output[0]


# --------------------------------------------------------------------------------
# > TestCases
# --------------------------------------------------------------------------------
class TestApiHealthcheck(SharedMixin, BaseTestCase):
    """TestCase for the 'api' action"""

    service = Service.API


class TestCacheHealthcheck(SharedMixin, BaseTestCase):
    """TestCase for the 'cache' action"""

    service = Service.CACHE


class TestDatabaseHealthcheck(SharedMixin, BaseTestCase):
    """TestCase for the 'database' action"""

    service = Service.DATABASE


class TestMigrationsHealthcheck(SharedMixin, BaseTestCase):
    """TestCase for the 'migrations' action"""

    service = Service.MIGRATIONS
