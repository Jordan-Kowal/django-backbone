"""Utility functions for the core API"""


# Django
from django.conf import settings

# Personal
from jklib.django.utils.emails import get_css_content
from jklib.django.utils.network import get_server_domain
from jklib.django.utils.templates import render_template


# --------------------------------------------------------------------------------
# > Internationalization
# --------------------------------------------------------------------------------
def render_email_template(template_path, context=None):
    """
    Renders an email template with extended context and custom CSS
    :param str template_path: Django path to the template file
    :param dict context: Context values for the template
    :return: Our dynamically-generated HTML
    :rtype: str
    """
    if context is None:
        context = {}
    additional_context = shared_email_context()
    full_context = {**additional_context, **context}  # Order matters
    return render_template(template_path, full_context)


def shared_email_context():
    """
    :return: Basic context to be used in emails
    :rtype: dict
    """
    return {
        "domain": get_server_domain(),
        "frontend_url": settings.FRONTEND_ROOT_URL,
        "css": get_css_content(settings.EMAIL_CSS),
    }
