"""Shared classes, functions, and constants for healthchecks services tests"""

# Personal
from jklib.django.drf.tests import ActionTestCase
from jklib.django.utils.tests import assert_logs

# --------------------------------------------------------------------------------
# > Constants
# --------------------------------------------------------------------------------
SERVICE_URL = "/api/healthchecks"


# --------------------------------------------------------------------------------
# > TestCase
# --------------------------------------------------------------------------------
class HealthcheckTestCase(ActionTestCase):
    """
    Base TestCase for healthcheck services
    Contains shared tests due to all healthcheck behaving the same way
    When using this class, make sure to override the PARAMETER values
    """

    error_code = 500
    success_code = 200

    # ----------------------------------------
    # Parameters
    # ----------------------------------------
    service = None
    service_base_url = None
    is_meta = True

    # ----------------------------------------
    # Behavior
    # ----------------------------------------
    def setUp(self):
        """Creates an admin and normal user"""
        self.admin = self.create_admin_user()
        self.user = self.create_user()
        super(HealthcheckTestCase, self).setUp()

    # ----------------------------------------
    # Properties
    # ----------------------------------------
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

    # ----------------------------------------
    # Tests
    # ----------------------------------------
    def test_permissions(self):
        """Tests that only an admin can access this service"""
        if not self.is_meta:
            self.assert_must_be_admin()

    def test_healthcheck_failure(self):
        """Cannot be tested"""
        pass

    def test_healthcheck_success(self):
        """Tests the service is working and the call appears in the logfile"""
        if not self.is_meta:
            self.client.force_authenticate(self.admin)
            self.assert_healthcheck_success()

    # ----------------------------------------
    # Assertion helpers
    # ----------------------------------------
    @assert_logs(logger="healthcheck", level="INFO")
    def assert_must_be_admin(self):
        """Tries to use the service logged out, as a user, and as an admin"""
        self.client.logout()
        response = self.client.get(self.service_base_url)
        assert response.status_code == 401
        # 403 Not admin
        self.client.force_authenticate(self.user)
        response = self.client.get(self.service_base_url)
        assert response.status_code == 403
        # 200 Admin
        self.client.logout()
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.service_base_url)
        assert response.status_code == self.success_code

    @assert_logs(logger="healthcheck", level="INFO")
    def assert_healthcheck_success(self):
        """Checks if a successful call correctly logs its results"""
        response = self.client.get(self.service_base_url)
        assert response.status_code == self.success_code
        assert self.success_message == self.logger_context.output[0]
