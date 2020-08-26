"""Utility functions for email management"""


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

    Parameters
    ----------
    template_path : str
        Django path to the template file
    context : dict
        Context values for the template

    Returns
    -------
    str
        Our dynamically-generated HTML
    """
    if context is None:
        context = {}
    additional_context = shared_email_context()
    full_context = {**additional_context, **context}  # Order matters
    return render_template(template_path, full_context)


def shared_email_context():
    """
    Returns some static context useful for email templates

    Returns
    -------
    dict
        Basic context to be used in emails
    """
    return {
        "backend_url": get_server_domain(),
        "frontend_url": settings.FRONTEND_ROOT_URL,
        "css": get_css_content(settings.EMAIL_CSS),
    }
