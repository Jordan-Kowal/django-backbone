"""Handler for the 'request_password_reset' action"""

# Django
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.serializers import EmailField
from rest_framework.status import HTTP_202_ACCEPTED

# Personal
from jklib.django.db.queries import get_object_or_none
from jklib.django.drf.actions import ActionHandler
from jklib.django.drf.serializers import NotEmptySerializer, required


# --------------------------------------------------------------------------------
# > Serializers
# --------------------------------------------------------------------------------
class RequestPasswordResetSerializer(NotEmptySerializer):
    """Simple form with only a required email address"""

    email = EmailField(**required())


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class RequestPasswordResetHandler(ActionHandler):
    """
    Using the provided email address, this service will:
        Fetch the user instance associated to this email
        Generate a security token for a password reset
        Send an email with this token/url to this email address
    For security reasons, it returns 200 OK even if no user was found with this email address
    Because we send the email asynchronously, it does not impact the response time
    """

    serializer_mode = "normal"
    serializer = RequestPasswordResetSerializer

    def main(self):
        """
        Sends a "password reset" email to the user, if he exists
        :return: A 202 HTTP response as the email is sent asynchronously
        :rtype: Response
        """
        serializer = self.get_valid_serializer(data=self.data)
        email = serializer.validated_data.get("email", None)
        user = get_object_or_none(User, email=email)
        if user is not None:
            user.profile.send_reset_password_email()
        return Response(None, HTTP_202_ACCEPTED)
