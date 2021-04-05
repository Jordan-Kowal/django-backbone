"""Shared constants, functions, and classes for our users application"""

# Built-in
from time import sleep

# Django
from django.contrib.auth.models import User
from django.core import mail


# --------------------------------------------------------------------------------
# > Assertions
# --------------------------------------------------------------------------------
def assert_user_email_was_sent(user, subject, async_=False, index=0, size=1):
    """
    Checks that one specific email has been sent to our user
    :param User user: The user that will receive the email
    :param str subject: The email subject
    :param bool async_: Whether the email was sent asynchronously
    :param int index: Expected index of our email in the outbox
    :param int size: Quantity of emails in the outbox
    """
    if async_:
        sleep(0.2)
    email = mail.outbox[index]
    assert len(email.to) == index
    assert len(mail.outbox) == size
    assert email.subject == subject
    assert email.to[0] == user.email
