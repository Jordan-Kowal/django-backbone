"""Factories for the `contact` app"""

# Third-party
import factory

# Local
from .models import Contact


# --------------------------------------------------------------------------------
# > Factories
# --------------------------------------------------------------------------------
class ContactFactory(factory.django.DjangoModelFactory):
    """Factory for the User model, to create non-admin users"""

    class Meta:
        model = Contact

    ip = factory.Sequence(lambda x: f"101.0.0.{x}")
    name = factory.Sequence(lambda x: f"Name {x}")
    email = factory.Sequence(lambda x: f"fake-email-{x}@fake-domain.com")
    subject = factory.Sequence(lambda x: f"Subject {x}")
    body = factory.Sequence(lambda x: f"Long enough body {x}")
    # Using model's defaults for:
    #   -> user
