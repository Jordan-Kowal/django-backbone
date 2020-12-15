"""Service actions for the 'contacts' API"""

# Local
from .create import CreateContactHandler
from .destroy import DestroyContactHandler
from .destroy_many import DestroyManyContactsHandler
from .list import ListContactHandler
from .retrieve import RetrieveContactHandler
