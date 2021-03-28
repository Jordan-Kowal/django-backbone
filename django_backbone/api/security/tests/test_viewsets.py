"""Tests for the 'security' app viewsets"""

# Built-in
from datetime import date, timedelta

# Personal
from jklib.django.drf.tests import ActionTestCase
from jklib.django.utils.tests import assert_logs

# Local
from ..models import NetworkRule

# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
SERVICE_URL = "/api/network_rules/"


class BaseTestCase(ActionTestCase):
    """Base class for all the NetworkRule action test cases"""

    def setUp(self):
        """Creates and authenticates an Admin user"""
        self.admin = self.create_admin_user(authenticate=True)

    @staticmethod
    def assert_instance_from_payload(instance, payload, mapping=None):
        """
        Compares the payload fields to an instance.
        :param NetworkRule instance: The related instance
        :param dict payload: The data sent in the request
        :param dict mapping: Used to map payload fieldnames with instance fieldnames
        """
        for field, value in payload.items():
            if field == "expires_on" and value is None:
                continue
            instance_field = field if mapping is None else mapping[field]
            instance_value = getattr(instance, instance_field, None)
            if instance_field == "expires_on":
                instance_value = instance_value.isoformat()
            assert value == instance_value

    @staticmethod
    def assert_instance_representation(network_rule, response_data):
        """
        Compares a response payload with a NetworkRule instance
        :param NetworkRule network_rule: NetworkRule instance from the database
        :param dict response_data: Response data from the API
        """
        expires_on = None
        if response_data["expires_on"] is not None:
            expires_on = date.fromisoformat(response_data["expires_on"])
        assert network_rule.id == response_data["id"]
        assert network_rule.ip == response_data["ip"]
        assert network_rule.status == response_data["status"]
        assert network_rule.expires_on == expires_on
        assert network_rule.active == response_data["active"]
        assert network_rule.comment == response_data["comment"]

    def assert_status_field_is_required(self, url, payload):
        """
        Checks that the status field is required
        :param str url: The target url
        :param dict payload: The data to pass to the request
        """
        temp_payload = payload.copy()
        # None
        temp_payload["status"] = None
        response = self.http_method(url, data=temp_payload)
        assert response.status_code == 400
        assert len(response.data["status"]) > 0
        # Empty String
        temp_payload["status"] = ""
        response = self.http_method(url, data=temp_payload)
        assert response.status_code == 400
        assert len(response.data["status"]) > 0
        # Missing
        del temp_payload["status"]
        response = self.http_method(url, temp_payload)
        assert response.status_code == 400
        assert len(response.data["status"]) > 0

    def assert_status_field_active_choices(self, url, payload):
        """
        Checks that the status can only be WHITELISTED or BLACKLISTED
        :param str url: The target url
        :param dict payload: The data to pass to the request
        """
        temp_payload = payload.copy()
        temp_payload["status"] = 0
        response = self.http_method(url, data=temp_payload)
        assert response.status_code == 400
        assert len(response.data["status"]) > 0
        for value in [1, 2]:
            temp_payload["ip"] = f"127.0.0.{value}"
            temp_payload["status"] = value
            response = self.http_method(url, data=temp_payload)
            assert response.status_code == self.success_code

    def assert_valid_expires_on(self, url, payload):
        """
        Checks that the provided date cannot be in the past
        :param str url: The target url
        :param dict payload: The data to pass to the request
        """
        temp_payload = payload.copy()
        # Invalid dates
        temp_payload["expires_on"] = (date.today() - timedelta(days=1)).isoformat()
        response = self.http_method(url, data=temp_payload)
        assert response.status_code == 400
        assert len(response.data["expires_on"]) > 0
        # Valid date
        temp_payload["expires_on"] = (date.today() + timedelta(days=1)).isoformat()
        response = self.http_method(url, data=temp_payload)
        assert response.status_code == self.success_code

    @staticmethod
    def create_network_rule(**kwargs):
        """
        Creates a NetworkRule instance using default parameters and the one provided
        :param kwargs: Parameters to override the default values
        :return: The created NetworkRule instance
        :rtype: NetworkRule
        """
        default_values = {
            "ip": "127.0.0.10",
            "status": NetworkRule.Status.NONE,
            "expires_on": date.today() + timedelta(days=60),
            "active": False,
            "comment": "Test",
        }
        data = {**default_values, **kwargs}
        return NetworkRule.objects.create(**data)


# --------------------------------------------------------------------------------
# > TestCases
# --------------------------------------------------------------------------------
class TestCreateNetworkRule(BaseTestCase):
    """TestCase for the 'create' action"""

    url_template = SERVICE_URL
    http_method_name = "POST"
    success_code = 201

    def setUp(self):
        """Creates and authenticates an Admin user, and prepares a valid payload"""
        super().setUp()
        self.payload = {
            "ip": "127.0.0.1",
            "status": 1,
            "expires_on": None,
            "active": False,
            "comment": "Test comment",
        }

    @assert_logs("security", "INFO")
    def test_permissions(self):
        """Tests that only admin users can access this service"""
        self.assert_admin_permissions(url=self.url(), payload=self.payload)
        assert NetworkRule.objects.count() == 1

    @assert_logs("security", "INFO")
    def test_expires_on(self):
        """Tests that you must provide a valid date in format and value"""
        self.assert_valid_expires_on(url=self.url(), payload=self.payload)

    @assert_logs("security", "INFO")
    def test_create_success(self):
        """Tests that we created a new NetworkRule successfully"""
        response = self.http_method(self.url(), data=self.payload)
        assert response.status_code == self.success_code
        assert NetworkRule.objects.count() == 1
        network_rule = NetworkRule.objects.get(pk=1)
        self.assert_instance_from_payload(network_rule, self.payload)
        self.assert_instance_representation(network_rule, response.data)


class TestListNetworkRules(BaseTestCase):
    """TestCase for the 'list' action"""

    url_template = SERVICE_URL
    http_method_name = "GET"
    success_code = 200

    def test_permissions(self):
        """Tests that only admin users can access this service"""
        assert NetworkRule.objects.count() == 0
        self.assert_admin_permissions(url=self.url())

    @assert_logs("security", "INFO")
    def test_success(self):
        """Tests that we get the list of NetworkRules"""
        response = self.http_method(self.url())
        assert response.status_code == self.success_code
        assert NetworkRule.objects.count() == len(response.data) == 0
        rule_1 = self.create_network_rule()
        rule_2 = self.create_network_rule(ip="127.0.0.2")
        response = self.http_method(self.url())
        assert response.status_code == self.success_code
        assert NetworkRule.objects.count() == len(response.data) == 2
        self.assert_instance_representation(rule_2, response.data[0])
        self.assert_instance_representation(rule_1, response.data[1])


class TestRetrieveNetworkRule(BaseTestCase):
    """TestCase for the 'retrieve' action"""

    url_template = f"{SERVICE_URL}/{{id}}/"
    http_method_name = "GET"
    success_code = 200

    @assert_logs("security", "INFO")
    def setUp(self):
        """Also creates a NetworkRule and builds its detail URL"""
        super().setUp()
        self.rule = self.create_network_rule()
        self.detail_url = self.url(context={"id": self.rule.id})

    def test_permissions(self):
        """Tests that only admin users can access this service"""
        assert NetworkRule.objects.count() == 1
        self.assert_admin_permissions(url=self.detail_url)

    def test_success(self):
        """Tests that we can retrieve a NetworkRule instance"""
        response = self.http_method(self.detail_url)
        assert response.status_code == self.success_code
        self.assert_instance_representation(self.rule, response.data)


class TestUpdateNetworkRule(BaseTestCase):
    """TestCase for the 'update' action"""

    url_template = f"{SERVICE_URL}/{{id}}/"
    http_method_name = "PUT"
    success_code = 200

    @assert_logs("security", "INFO")
    def setUp(self):
        """Creates 1 admin, 1 rule, and a valid payload"""
        super().setUp()
        self.rule = self.create_network_rule()
        self.detail_url = self.url(context={"id": self.rule.id})
        self.payload = {
            "ip": "128.0.0.1",
            "status": 2,
            "expires_on": None,
            "active": False,
            "comment": "Test comment",
        }

    @assert_logs("security", "INFO")
    def test_permissions(self):
        """Tests that only admin users can access this service"""
        assert NetworkRule.objects.count() == 1
        self.assert_admin_permissions(url=self.detail_url, payload=self.payload)

    @assert_logs("security", "INFO")
    def test_expires_on(self):
        """Tests that you must provide a valid date in format and value"""
        self.assert_valid_expires_on(url=self.detail_url, payload=self.payload)

    @assert_logs("security", "INFO")
    def test_success(self):
        """Tests that we updated a NetworkRule successfully"""
        response = self.http_method(self.detail_url, data=self.payload)
        assert response.status_code == self.success_code
        network_rule = NetworkRule.objects.get(pk=1)
        self.assert_instance_from_payload(network_rule, self.payload)
        self.assert_instance_representation(network_rule, response.data)


class TestDestroyNetworkRule(BaseTestCase):
    """TestCase for the 'destroy' action"""

    url_template = f"{SERVICE_URL}/{{id}}/"
    http_method_name = "DELETE"
    success_code = 204

    @assert_logs("security", "INFO")
    def setUp(self):
        """Also creates 2 NetworkRules"""
        super().setUp()
        self.rule_1 = self.create_network_rule()
        self.rule_2 = self.create_network_rule(ip="127.0.0.2")
        self.detail_url_1 = self.url(context={"id": self.rule_1.id})
        self.detail_url_2 = self.url(context={"id": self.rule_2.id})

    @assert_logs("security", "INFO")
    def test_permissions(self):
        """Tests that only admin users can access this service"""
        assert NetworkRule.objects.count() == 2
        self.assert_admin_permissions(url=self.detail_url_1)
        assert NetworkRule.objects.count() == 1

    @assert_logs("security", "INFO")
    def test_success(self):
        """Tests that you can successfully delete a NetworkRule instance"""
        assert NetworkRule.objects.count() == 2
        response = self.http_method(self.detail_url_1)
        assert response.status_code == self.success_code
        assert NetworkRule.objects.count() == 1
        response = self.http_method(self.detail_url_2)
        assert response.status_code == self.success_code
        assert NetworkRule.objects.count() == 0


class TestBulkDestroyNetworkRules(BaseTestCase):
    """TestCase for the 'bulk_destroy' action"""

    url_template = SERVICE_URL
    http_method_name = "DELETE"
    success_code = 204

    @assert_logs("security", "INFO")
    def setUp(self):
        """Also creates 4 NetworkRules"""
        super().setUp()
        for i in range(1, 5):
            self.create_network_rule(ip=f"127.0.0.1{i}")

    @assert_logs("security", "INFO")
    def test_permissions(self):
        """Tests that only admin users can access this service"""
        assert NetworkRule.objects.count() == 4
        payload = {"ids": [1, 3]}
        self.assert_admin_permissions(url=self.url(), payload=payload)
        assert NetworkRule.objects.count() == 2

    @assert_logs("security", "INFO")
    def test_success(self):
        """Tests that we can delete several NetworkRules"""
        # Only valid IDs
        payload = {"ids": [1, 4]}
        response = self.http_method(self.url(), data=payload)
        assert response.status_code == self.success_code
        assert NetworkRule.objects.count() == 2
        # Some valid IDs
        payload = {"ids": [2, 6]}
        response = self.http_method(self.url(), data=payload)
        assert response.status_code == self.success_code
        assert NetworkRule.objects.count() == 1
        assert NetworkRule.objects.first().id == NetworkRule.objects.last().id == 3


class TestClearNetworkRule(BaseTestCase):
    """TestCase for the 'clear' action"""

    url_template = f"{SERVICE_URL}/{{id}}/clear/"
    http_method_name = "PUT"
    success_code = 200

    @assert_logs("security", "INFO")
    def setUp(self):
        """Also creates 1 NetworkRule"""
        super().setUp()
        self.rule = self.create_network_rule()
        self.rule_url = self.url(context={"id": self.rule.id})

    @assert_logs("security", "INFO")
    def test_permissions(self):
        """Tests that only admin users can access this service"""
        assert NetworkRule.objects.count() == 1
        self.assert_admin_permissions(url=self.rule_url)

    @assert_logs("security", "INFO")
    def test_success(self):
        """Tests that we can clear a NetworkRule"""
        self.rule.blacklist()
        assert self.rule.is_blacklisted
        response = self.http_method(self.rule_url)
        assert response.status_code == self.success_code
        updated_rule_1 = NetworkRule.objects.get(pk=self.rule.id)
        assert not updated_rule_1.is_blacklisted
        assert updated_rule_1.expires_on is None
        assert not updated_rule_1.active
        assert updated_rule_1.status == NetworkRule.Status.NONE
        self.assert_instance_representation(updated_rule_1, response.data)


class TestBulkClearNetworkRule(BaseTestCase):
    """TestCase for the 'bulk_clear' action"""

    url_template = f"{SERVICE_URL}/clear/"
    http_method_name = "POST"
    success_code = 204

    @assert_logs("security", "INFO")
    def setUp(self):
        """Also creates a lot of instances for us to clear"""
        super().setUp()
        self._generate_instances()

    @assert_logs("security", "INFO")
    def test_permissions(self):
        """Tests that only admin users can access this service"""
        self.assert_admin_permissions(url=self.url())

    @assert_logs("security", "INFO")
    def test_status_field(self):
        """Tests the status field is optional and only accept specific values"""
        # Can be missing
        response = self.http_method(self.url())
        assert response.status_code == self.success_code
        response = self.http_method(self.url(), data={"status": None})
        assert response.status_code == self.success_code
        # Invalid status
        response = self.http_method(self.url(), data={"status": 40})
        assert response.status_code == 400
        assert len(response.data["status"]) > 0
        # Valid status
        response = self.http_method(self.url(), data={"status": 2})
        assert response.status_code == self.success_code

    @assert_logs("security", "INFO")
    def test_success_on_none(self):
        """Tests that the NONE rules were cleared"""
        response = self.http_method(self.url(), data={"status": 0})
        assert response.status_code == self.success_code
        self._assert_clears([True, True, False, False, False, False])

    @assert_logs("security", "INFO")
    def test_success_on_whitelisted(self):
        """Tests that the WHITELISTED rules were cleared"""
        response = self.http_method(self.url(), data={"status": 1})
        assert response.status_code == self.success_code
        self._assert_clears([False, False, True, True, False, False])

    @assert_logs("security", "INFO")
    def test_success_on_blacklisted(self):
        """Tests that the BLACKLISTED rules were cleared"""
        response = self.http_method(self.url(), data={"status": 2})
        assert response.status_code == self.success_code
        self._assert_clears([False, False, False, False, True, True])

    @assert_logs("security", "INFO")
    def test_success_no_status(self):
        """Tests that all clearable  rules were cleared"""
        response = self.http_method(self.url())
        assert response.status_code == self.success_code
        self._assert_clears([True, True, True, True, True, True])

    @staticmethod
    def _assert_clears(predictions):
        """
        Compares our predictions with the existing rules on whether they were cleared
        :param [bool] predictions: Prediction of `is_cleared` for each existing instance
        """
        instances = NetworkRule.objects.all().order_by("id")
        for instance, prediction in zip(instances, predictions):
            is_cleared = (
                not instance.active
                and instance.expires_on is None
                and instance.status == NetworkRule.Status.NONE
            )
            assert prediction == is_cleared

    def _generate_instances(self):
        """Creates 6 clearable NetworkRule instances"""
        end_date = date.today() + timedelta(days=60)
        for i in range(6):
            self.create_network_rule(
                ip=f"{i+1}.0.0.{i+1}",
                active=True,
                expires_on=end_date,
                status=NetworkRule.Status.values[i // 2],
            )


class TestActivateNewNetworkRule(BaseTestCase):
    """TestCase for the 'activate_new' action"""

    url_template = f"{SERVICE_URL}/activate/"
    http_method_name = "POST"
    success_code = 201

    def setUp(self):
        """Also prepares a payload"""
        super().setUp()
        self.payload = {
            "ip": "127.0.0.1",
            "expires_on": None,
            "comment": "",
            "status": 1,
        }

    @assert_logs("security", "INFO")
    def test_permissions(self):
        """Tests that only admin users can access this service"""
        self.assert_admin_permissions(url=self.url(), payload=self.payload)

    @assert_logs("security", "INFO")
    def test_expires_on(self):
        """Tests that you must provide a valid date in format and value"""
        self.assert_valid_expires_on(url=self.url(), payload=self.payload)

    def test_status_field_is_required(self):
        """Test that the status field is required"""
        # None
        self.payload["status"] = None
        response = self.http_method(self.url(), data=self.payload)
        assert response.status_code == 400
        # Empty String
        self.payload["status"] = ""
        response = self.http_method(self.url(), data=self.payload)
        assert response.status_code == 400
        # Missing
        del self.payload["status"]
        response = self.http_method(self.url(), data=self.payload)
        assert response.status_code == 400
        assert len(response.data["status"]) > 0

    @assert_logs("security", "INFO")
    def test_status_field(self):
        """Tests is required and has limited choices"""
        self.assert_status_field_is_required(self.url(), self.payload)
        assert NetworkRule.objects.count() == 0
        self.assert_status_field_active_choices(self.url(), self.payload)
        assert NetworkRule.objects.count() == 2

    @assert_logs("security", "INFO")
    def test_success(self):
        """Tests we can create a WHITELISTED or BLACKLISTED rule"""
        # Whitelisted
        self.payload["status"] = 1
        response = self.http_method(self.url(), data=self.payload)
        assert response.status_code == self.success_code
        assert NetworkRule.objects.count() == 1
        rule_1 = NetworkRule.objects.get(pk=1)
        self.assert_instance_from_payload(rule_1, self.payload)
        self.assert_instance_representation(rule_1, response.data)
        # Blacklisted
        self.payload["ip"] = "127.0.0.2"
        self.payload["expires_on"] = (date.today() + timedelta(days=10)).isoformat()
        self.payload["comment"] = "Comment 1"
        self.payload["status"] = 2
        response = self.http_method(self.url(), data=self.payload)
        assert response.status_code == self.success_code
        assert NetworkRule.objects.count() == 2
        rule_2 = NetworkRule.objects.get(pk=2)
        self.assert_instance_from_payload(rule_2, self.payload)
        self.assert_instance_representation(rule_2, response.data)


class TestActivateExistingNetworkRule(BaseTestCase):
    """TestCase for the 'activate_existing' action"""

    url_template = f"{SERVICE_URL}/{{id}}/activate/"
    http_method_name = "PUT"
    success_code = 200

    @assert_logs("security", "INFO")
    def setUp(self):
        """Also creates a NetworkRule and a payload to activate it"""
        super().setUp()
        self.rule = self.create_network_rule()
        self.detail_url = self.url(context={"id": self.rule.id})
        self.payload = {
            "override": False,
            "expires_on": None,
            "comment": "",
            "status": 1,
        }

    @assert_logs("security", "INFO")
    def test_permissions(self):
        """Tests that only admin users can access this service"""
        self.assert_admin_permissions(url=self.detail_url, payload=self.payload)

    @assert_logs("security", "INFO")
    def test_expires_on(self):
        """Tests that you must provide a valid date in format and value"""
        self.assert_valid_expires_on(url=self.detail_url, payload=self.payload)

    @assert_logs("security", "INFO")
    def test_status_field(self):
        """Tests is required and has limited choices"""
        self.payload["override"] = True
        self.assert_status_field_is_required(self.detail_url, self.payload)
        self.assert_status_field_active_choices(self.detail_url, self.payload)
        assert NetworkRule.objects.count() == 1

    @assert_logs("security", "INFO")
    def test_success_blacklist_with_override(self):
        """Tests `override` is required to blacklist a whitelisted rule"""
        self.rule.whitelist(override=True)
        # Without override
        self.payload["override"] = False
        self.payload["status"] = NetworkRule.Status.BLACKLISTED
        response = self.http_method(self.detail_url, data=self.payload)
        assert response.status_code == 409
        updated_rule = NetworkRule.objects.get(id=self.rule.id)
        assert updated_rule.is_whitelisted
        # With override
        self.payload["override"] = True
        response = self.http_method(self.detail_url, data=self.payload)
        assert response.status_code == self.success_code
        updated_rule = NetworkRule.objects.get(id=self.rule.id)
        assert updated_rule.is_blacklisted
        del self.payload["override"]
        self.assert_instance_from_payload(updated_rule, self.payload)
        self.assert_instance_representation(updated_rule, response.data)

    @assert_logs("security", "INFO")
    def test_success_whitelist_with_override(self):
        """Tests `override` is required to whitelist a blacklisted rule"""
        self.rule.blacklist(override=True)
        # Without override
        self.payload["override"] = False
        self.payload["status"] = NetworkRule.Status.WHITELISTED
        response = self.http_method(self.detail_url, data=self.payload)
        assert response.status_code == 409
        updated_rule = NetworkRule.objects.get(id=self.rule.id)
        assert updated_rule.is_blacklisted
        # With override
        self.payload["override"] = True
        response = self.http_method(self.detail_url, data=self.payload)
        assert response.status_code == self.success_code
        updated_rule = NetworkRule.objects.get(id=self.rule.id)
        assert updated_rule.is_whitelisted
        del self.payload["override"]
        self.assert_instance_from_payload(updated_rule, self.payload)
        self.assert_instance_representation(updated_rule, response.data)

    @assert_logs("security", "INFO")
    def test_success(self):
        """Test basic activation without override"""
        del self.payload["override"]
        # Whitelisting
        self.payload["status"] = NetworkRule.Status.WHITELISTED
        response = self.http_method(self.detail_url, data=self.payload)
        assert response.status_code == self.success_code
        updated_rule = NetworkRule.objects.get(id=self.rule.id)
        assert updated_rule.is_whitelisted
        self.assert_instance_from_payload(updated_rule, self.payload)
        self.assert_instance_representation(updated_rule, response.data)
        updated_rule.clear()
        # Blacklisting
        self.payload["status"] = NetworkRule.Status.BLACKLISTED
        response = self.http_method(self.detail_url, data=self.payload)
        assert response.status_code == self.success_code
        updated_rule = NetworkRule.objects.get(id=self.rule.id)
        assert updated_rule.is_blacklisted
        self.assert_instance_from_payload(updated_rule, self.payload)
        self.assert_instance_representation(updated_rule, response.data)
