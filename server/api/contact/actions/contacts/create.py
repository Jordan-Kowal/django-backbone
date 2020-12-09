"""Handler for the 'create' action"""

# Built-in
from datetime import date, timedelta

# Django
from rest_framework.response import Response
from rest_framework.serializers import BooleanField, CharField, EmailField
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN

# Personal
from jklib.django.drf.actions import ActionHandler, SerializerMode
from jklib.django.drf.serializers import ImprovedSerializer, required
from jklib.django.utils.network import get_client_ip

# Application
from api.contact.models import Contact
from api.core.models import IpAddress


# --------------------------------------------------------------------------------
# > Serializer
# --------------------------------------------------------------------------------
class CreateContactSerializer(ImprovedSerializer):
    """
    Serializer to create a new contact entry via the API
    Only in charge of data validation. The actual creation happens in the CreateContactHandler
    """

    name = CharField(
        min_length=Contact.NAME_LENGTH[0],
        max_length=Contact.NAME_LENGTH[1],
        **required()
    )
    email = EmailField(**required())
    subject = CharField(
        min_length=Contact.SUBJECT_LENGTH[0],
        max_length=Contact.SUBJECT_LENGTH[1],
        **required()
    )
    body = CharField(
        min_length=Contact.BODY_LENGTH[0],
        max_length=Contact.BODY_LENGTH[1],
        **required()
    )
    notify_user = BooleanField(default=False)


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class CreateContactHandler(ActionHandler):
    """Creates a contact instance and sends notification emails"""

    serializer_mode = SerializerMode.UNIQUE
    serializer = CreateContactSerializer

    def main(self):
        """
        Creates a contact message request and send notification emails
        User might get ban if he sends too many contact messages
        :return: HTTP 204 response without data
        :rtype: Response
        """
        serializer = self.get_valid_serializer(data=self.data)
        notify_user = serializer.validated_data.pop("notify_user")
        ip = get_client_ip(self.request)
        user = None if self.user.is_anonymous else self.user
        instance = Contact(ip=ip, user=user, **serializer.validated_data)
        if instance.should_ban_ip():
            ban_settings = Contact.get_ban_settings()
            ban_end_date = date.today() + timedelta(
                days=ban_settings["duration_in_days"]
            )
            IpAddress.blacklist_from_request(
                request=self.request,
                end_date=ban_end_date,
                comment="Too many requests in the Contact API",
            )
            return Response(None, status=HTTP_403_FORBIDDEN)
        else:
            instance.save()
            instance.send_notifications(True, notify_user)
            return Response(None, status=HTTP_204_NO_CONTENT)
