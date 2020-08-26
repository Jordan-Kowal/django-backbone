"""Django's command-line utility for administrative tasks."""

# Built-in
import os
import sys


# --------------------------------------------------------------------------------
# > Functions
# --------------------------------------------------------------------------------
def main():
    """Main runner for django"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server_config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
