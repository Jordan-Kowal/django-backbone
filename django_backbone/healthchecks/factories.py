"""Factories for the `healthchecks` app"""

# Third-party
import factory

# Local
from .models import HealthcheckDummy


# --------------------------------------------------------------------------------
# > Factories
# --------------------------------------------------------------------------------
class HealthcheckDummyFactory(factory.django.DjangoModelFactory):
    """Factory for the HealthcheckDummy model"""

    class Meta:
        model = HealthcheckDummy

    content = factory.Sequence(lambda x: f"Automatically generated content {x}")
