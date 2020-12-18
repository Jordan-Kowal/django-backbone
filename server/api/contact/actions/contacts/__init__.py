"""Service actions for the 'contacts' API"""

# Local
from .bulk_destroy import BulkDestroyContactsHandler
from .create import CreateContactHandler
from .destroy import DestroyContactHandler
from .list import ListContactHandler
from .retrieve import RetrieveContactHandler
