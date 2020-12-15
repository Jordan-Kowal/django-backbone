"""Handler for the 'delete_many' action"""

# Django
from rest_framework.response import Response

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode
from jklib.django.drf.serializers import IdListSerializer


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class DestroyManyContactsHandler(ModelActionHandler):
    """
    Action to delete multiple instances of a model when provided with valid IDs
    It uses the viewset's queryset as a starting point for the search
    """

    serializer_mode = SerializerMode.UNIQUE
    serializer = IdListSerializer

    def main(self):
        """
        Filters the instances with the provided IDs and removes them
        :return: HTTP 204 response without data
        :rtype: Response
        """
        return self.model_bulk_destroy()
