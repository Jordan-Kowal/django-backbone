"""Handler for the 'cache' healthcheck"""

# Built-in
from secrets import token_urlsafe

# Django
from django.core.cache import cache

# Local
from ._shared import HealthCheckHandler, Service


# --------------------------------------------------------------------------------
# > Handler
# --------------------------------------------------------------------------------
class CacheHealthCheckHandler(HealthCheckHandler):
    """Checks the cache is working properly by setting, fetching, and removing a key/value pair"""

    service = Service.CACHE

    def main(self):
        """
        Tries to set, read, and delete a key/value pair in the cache system
        :raises KeyError: Failed to set the key
        :raises ValueError: Key was set but with invalid value
        :raises AttributeError: Failed to remove the key
        """
        self.random_cache_key = token_urlsafe(30)
        self.random_cache_value = token_urlsafe(30)
        self._set_cache_value()
        self._remove_cached_value()

    # ----------------------------------------
    # Private
    # ----------------------------------------
    def _set_cache_value(self):
        """
        Tries to set a key/value pair in the cache
        :raises KeyError: If the cache key was not set
        :raises ValueError: If we did not found the expected value for our key
        """
        cache.set(self.random_cache_key, self.random_cache_value)
        cached_value = cache.get(self.random_cache_key, None)
        if cached_value is None:
            raise KeyError(f"Failed to set a key/value pair in the cache")
        if cached_value != self.random_cache_value:
            raise ValueError(
                f"Unexpected value stored in the '{self.random_cache_key}' cache key"
            )

    def _remove_cached_value(self):
        """
        Tries to remove the key from the cache
        :raises AttributeError: If failed to delete our key in the cache
        """
        cache.delete(self.random_cache_value)
        cached_value = cache.get(self.random_cache_value, None)
        if cached_value is not None:
            raise AttributeError(
                f"Failed to properly delete the '{self.random_cache_key}' key in the cache"
            )
