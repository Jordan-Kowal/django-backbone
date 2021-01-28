"""Service actions from the "ips" management API"""

# Local
from .blacklist_existing import BlacklistNetworkRuleHandler
from .blacklist_new import NewBlacklistNetworkRuleHandler
from .bulk_destroy import BulkDestroyNetworkRulesHandler
from .clear import ClearNetworkRuleHandler
from .clear_all import ClearAllNetworkRulesHandler
from .create import CreateNetworkRuleHandler
from .destroy import DestroyNetworkRuleHandler
from .list import ListNetworkRulesHandler
from .retrieve import RetrieveNetworkRuleHandler
from .update import UpdateNetworkRuleHandler
from .whitelist_existing import WhitelistNetworkRuleHandler
from .whitelist_new import NewWhitelistNetworkRuleHandler
