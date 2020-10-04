"""Handler for the 'delete' action"""

# Personal
from jklib.django.drf.actions import ModelActionHandler, SerializerMode


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class DestroyUserHandler(ModelActionHandler):
    """Deletes a user from the database"""

    serializer_mode = SerializerMode.NONE
    serializer = None

    def main(self):
        """
        Deletes the targeted user model
        :return: HTTP 204 response with no data
        :rtype: Response
        """
        return self.model_destroy()
