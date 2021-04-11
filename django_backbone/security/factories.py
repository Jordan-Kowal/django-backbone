"""Factories for the `users` app"""

# Built-in
from secrets import token_urlsafe

# Third-party
import factory

# Application
from users.factories import UserFactory

# Local
from .models import NetworkRule, SecurityToken


# --------------------------------------------------------------------------------
# > Factories
# --------------------------------------------------------------------------------
class NetworkRuleFactory(factory.django.DjangoModelFactory):
    """Factory for the NetworkRule model"""

    class Meta:
        model = NetworkRule

    ip = factory.Sequence(lambda x: f"100.0.0.{x}")
    comment = factory.Sequence(lambda x: f"NetworkRule Comment {x}")
    # Using model's defaults for:
    #   -> status
    #   -> expires_on
    #   -> active

    @factory.post_generation
    def do_blacklist(self, create, extracted, **kwargs):
        """Blacklists the IP address once it's created using the default duration"""
        if create and extracted:
            self.blacklist()

    @factory.post_generation
    def do_whitelist(self, create, extracted, **kwargs):
        """Whitelists the IP address once it's created using the default duration"""
        if create and extracted:
            self.whitelist()


class SecurityTokenFactory(factory.django.DjangoModelFactory):
    """Factory for the SecurityToken model"""

    class Meta:
        model = SecurityToken

    user = factory.SubFactory(UserFactory)
    type = "factory"
    value = factory.LazyFunction(lambda: token_urlsafe(50))
    # Using model's defaults for:
    #   -> expired_at
    #   -> used_at
    #   -> is_active_token
