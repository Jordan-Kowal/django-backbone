"""Handler for the 'destroy' action"""

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class DestroyContactHandler(ModelActionHandler):
    """Deletes an existing Contact instance"""

    serializer_mode = SerializerMode.NONE
    serializer = None

    def main(self):
        """
        Deletes the related Contact instance and returns a 204
        :return: HTTP 204 response without data
        :rtype: Response
        """
        return self.model_destroy()
