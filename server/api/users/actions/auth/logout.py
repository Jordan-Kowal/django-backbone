"""LogoutAction"""

# Django
from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

# Personal
from jklib.django.drf.actions import ActionHandler


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class LogoutHandler(ActionHandler):
    """Action to logout the current user"""

    serializer = None

    def main(self):
        """Logouts the current user"""
        logout(self.request)
        return Response(None, status=HTTP_200_OK)
