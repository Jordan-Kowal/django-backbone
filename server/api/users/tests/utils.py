"""Shared constants, functions, and classes for our users application"""

# Built-in
from time import sleep

# Django
from django.contrib.auth.models import User
from django.core import mail


# --------------------------------------------------------------------------------
# > Assertions
# --------------------------------------------------------------------------------
def assert_user_email_was_sent(user, subject):
    """
    Checks that one specific email has been sent to our user
    :param User user: The user that will receive the email
    :param str subject: The email subject
    """
    sleep(0.2)
    email = mail.outbox[0]
    assert len(email.to) == 1
    assert len(mail.outbox) == 1
    assert email.subject == subject
    assert email.to[0] == user.email
