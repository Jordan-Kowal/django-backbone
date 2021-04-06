"""Models for the 'healthchecks' app"""


# Django
from django.db.models import CharField, Model


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class HealthcheckDummy(Model):
    """Dummy model used during the database healthcheck"""

    content = CharField(max_length=100, verbose_name="Content")

    class Meta:
        db_table = "healthcheck_dummies"
        indexes = []
        ordering = ["-id"]
        verbose_name = "Healthcheck Dummy"
        verbose_name_plural = "Healthcheck Dummies"
