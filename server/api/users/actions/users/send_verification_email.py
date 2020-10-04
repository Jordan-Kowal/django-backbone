"""Handler for the 'send_verification_email' action"""

# Django
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

# Personal
from jklib.django.drf.actions import ActionHandler, SerializerMode


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class SendVerificationEmailHandler(ActionHandler):
    """
    Sends the 'verification email' to the targeted user
    (It will automatically generate a new unique token/link sent in the email)
    """

    serializer_mode = SerializerMode.NONE
    serializer = None

    def main(self):
        """
        Sends the 'verification email' to the authenticated user
        :return: A 204 HTTP response as the email is sent synchronously
        :rtype: Response
        """
        user = self.viewset.get_object()
        user.profile.send_verification_email(async_=False)
        return Response(None, HTTP_204_NO_CONTENT)
