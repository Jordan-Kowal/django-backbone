"""Viewsets for the 'healthchecks' app"""

# Built-in
import logging
from enum import Enum
from functools import wraps
from secrets import token_urlsafe

# Django
from django.core.cache import cache
from django.core.exceptions import FieldError, ImproperlyConfigured, ObjectDoesNotExist
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

# Personal
from jklib.django.drf.permissions import IsAdminUser
from jklib.django.drf.viewsets import ImprovedViewSet

# Local
from .models import HealthcheckDummy

# --------------------------------------------------------------------------------
# > Utilities
# --------------------------------------------------------------------------------
LOGGER = logging.getLogger("healthcheck")


class Service(Enum):
    """List of services with healthchecks"""

    API = "API"
    CACHE = "CACHE"
    DATABASE = "DATABASE"
    MIGRATIONS = "MIGRATIONS"


def error_catcher(service):
    """
    Decorator for the healthchecks API endpoints
    Logs the API call result, and returns a 500 if the service crashes
    :param Service service: Which service is called
    :return: Either the service success Response or a 500
    :rtype: Response
    """

    def decorator(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            try:
                response = function(request, *args, **kwargs)
                LOGGER.info(f"Service {service.name} is OK")
                return response
            except Exception as error:
                LOGGER.error(f"Service {service.name} is KO: {error}")
                return Response(None, status=HTTP_500_INTERNAL_SERVER_ERROR)

        return wrapper

    return decorator


# --------------------------------------------------------------------------------
# > ViewSets
# --------------------------------------------------------------------------------
class HealthcheckViewSet(ImprovedViewSet):
    """Viewset for our various healthchecks"""

    viewset_permission_classes = (IsAdminUser,)
    serializer_classes = {"default": None}

    @action(detail=False, methods=["get"])
    @error_catcher(Service.API)
    def api(self, request):
        """Checks if the API is up and running"""
        return Response(None, status=HTTP_200_OK)

    @action(detail=False, methods=["get"])
    @error_catcher(Service.CACHE)
    def cache(self, request):
        """Checks we can write/read/delete in the cache system"""
        random_cache_key = token_urlsafe(30)
        random_cache_value = token_urlsafe(30)
        # Set value
        cache.set(random_cache_key, random_cache_value)
        cached_value = cache.get(random_cache_key, None)
        if cached_value is None:
            raise KeyError(f"Failed to set a key/value pair in the cache")
        if cached_value != random_cache_value:
            raise ValueError(
                f"Unexpected value stored in the '{random_cache_key}' cache key"
            )
        # Get value
        cache.delete(random_cache_value)
        cached_value = cache.get(random_cache_value, None)
        if cached_value is not None:
            raise AttributeError(
                f"Failed to properly delete the '{random_cache_key}' key in the cache"
            )
        return Response(None, status=HTTP_200_OK)

    @action(detail=False, methods=["get"])
    @error_catcher(Service.DATABASE)
    def database(self, request):
        """Checks we can write/read/delete in the database"""
        # Create
        content = token_urlsafe(50)
        instance = HealthcheckDummy.objects.create(content=content)
        if instance is None:
            raise LookupError("Failed to create the HealthcheckDummy instance")
        # Get
        fetched_instance = HealthcheckDummy.objects.get(pk=instance.id)
        if fetched_instance is None:
            raise ObjectDoesNotExist(
                "Failed to fetch the created HealthcheckDummy instance"
            )
        if fetched_instance.content != content:
            raise FieldError(
                "Unexpected field value for the fetched HealthcheckDummy instance"
            )
        # Delete
        HealthcheckDummy.objects.all().delete()
        if HealthcheckDummy.objects.count() > 0:
            raise RuntimeError(
                "Failed to properly delete all HealthcheckDummy instances"
            )
        return Response(None, status=HTTP_200_OK)

    @action(detail=False, methods=["get"])
    @error_catcher(Service.MIGRATIONS)
    def migrations(self, request):
        """Checks if all migrations have been applied to our database"""
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            raise ImproperlyConfigured("There are migrations to apply")
        return Response(None, status=HTTP_200_OK)
