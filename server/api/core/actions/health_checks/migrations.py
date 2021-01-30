"""Handler for the 'migrations' healthcheck"""

# Django
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

# Local
from ._shared import HealthCheckHandler, Service


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class MigrationsHealthCheckHandler(HealthCheckHandler):
    """Checks if all migrations have been applied to our database"""

    service = Service.MIGRATIONS

    def main(self):
        """
        Checks if there are not-yet-applied migrations
        :raises ImproperlyConfigured: If some migrations have not been applied
        """
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            raise ImproperlyConfigured("There are migrations to apply")
