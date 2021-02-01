"""HealthcheckDummy"""

# Django
from django.db.models import CharField, Model


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class HealthcheckDummy(Model):
    """
    Dummy model whose sole purpose is to be used during the database healthcheck
    in order to perform write, update, and delete operations
    and make sure the database is working properly
    """

    content = CharField(max_length=100, verbose_name="Content")

    class Meta:
        """Meta class to setup our database table"""

        db_table = "core_healthcheck_dummies"
        indexes = []
        ordering = ["-id"]
        verbose_name = "Healthcheck Dummy"
        verbose_name_plural = "Healthcheck Dummies"
