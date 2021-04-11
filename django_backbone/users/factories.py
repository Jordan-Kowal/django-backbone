"""Factories for the `users` app"""

# Third-party
import factory

# Local
from .models import User


# --------------------------------------------------------------------------------
# > Factories
# --------------------------------------------------------------------------------
class UserFactory(factory.django.DjangoModelFactory):
    """Factory for the User model, to create non-admin users"""

    class Meta:
        model = User
        exclude = ("is_staff", "is_superuser")

    email = factory.Sequence(lambda x: f"fake-email-{x}@fake-domain.com")
    password = factory.Sequence(lambda x: f"Str0ngP4ssw0rd!{x}")
    first_name = factory.Sequence(lambda x: f"Firstname{x}")
    last_name = factory.Sequence(lambda x: f"Lastname{x}")
    is_staff = False
    is_superuser = False
    # Using model's defaults for:
    #   -> date_joined
    #   -> is_active
    #   -> is_verified

    @factory.post_generation
    def set_password(self, create, extracted, **kwargs):
        """Sets the user's password correctly post creation"""
        self.set_password(self.password)
        self.save()


class AdminFactory(UserFactory):
    """Factory to create admins"""

    class Meta:
        model = User
        exclude = ("is_superuser",)

    is_staff = True


class SuperUserFactory(UserFactory):
    """Factory to create superusers"""

    class Meta:
        model = User
        exclude = tuple()

    is_staff = True
    is_superuser = True
