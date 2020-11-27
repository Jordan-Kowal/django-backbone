"""
TEMPLATE FOR THE `local_settings`.py file
DO NOT PUT YOUR INFORMATION IN THIS FILE

Create a new `local_settings.py` and replace whichever values you need in it
Note that `local_settings.py` is part of the `.gitignore` (for security reasons)
"""


# Built-in
import os

# --------------------------------------------------------------------------------
# > Security
# --------------------------------------------------------------------------------
# Generic
SECRET_KEY = "fake secret key you should replace"

# URLs
ALLOWED_HOSTS = []
FRONTEND_ROOT_URL = "127.0.0.1"
DEBUG = True
SECURE_SSL_REDIRECT = False

# Cookies
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False

# Session
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# --------------------------------------------------------------------------------
# > Database
# --------------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "database.sqlite3"),
    }
}


# --------------------------------------------------------------------------------
# > Email server
# --------------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "fake_email@fake_domain.com"
EMAIL_HOST_PASSWORD = "fake password"


# --------------------------------------------------------------------------------
# > Custom Django Commands
# --------------------------------------------------------------------------------
SUPER_USER = {
    "username": "fake_email@fake_domain.com",
    "password": "fake password",
    "email": "fake_email@fake_domain.com",
}
