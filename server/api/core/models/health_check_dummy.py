"""HealthCheckDummy"""

# Django
from django.db.models import CharField, Model


# --------------------------------------------------------------------------------
# > Models
# --------------------------------------------------------------------------------
class HealthCheckDummy(Model):
    """
    Dummy model whose sole purpose is to be used during the database healthcheck
    in order to perform write, update, and delete operations
    and make sure the database is working properly
    """

    content = CharField(max_length=100)

    class Meta:
        """Meta class to setup our database table"""

        db_table = "core_health_check_dummies"
        indexes = []
        ordering = ["-id"]
        verbose_name = "Health Check Dummy"
        verbose_name_plural = "Health Check Dummies"
