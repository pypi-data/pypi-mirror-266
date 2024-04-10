class KarabinerConfigFileError(Exception):
    pass


# Import everything that someone else may want to use
from .keyboard_base import KeyResolver, NoKeyMappingFoundError, CharRequiresMultipleKeys
from .keyboard_us import RESOLVER_US_MAC, RESOLVER_US_LINUX
from .keyboard_de import RESOLVER_DE_LINUX
from .rules import helper_insert_rule_into_config
from .script_utils import helper_default_argument_parser_action_handler


_RESOLVERS: dict[str,KeyResolver] = {
    "us_mac": RESOLVER_US_MAC,
    "us_linux": RESOLVER_US_LINUX,
    "de_linux": RESOLVER_DE_LINUX,
}

class NoResolverWithName(Exception):
    pass

def get_resolver(name: str) -> KeyResolver:
    if result := _RESOLVERS.get(name):
        return result
    else:
        raise NoResolverWithName(f"No resolver/keyboard layout with the value '{name}' found. Valid values are {', '.join(_RESOLVERS.keys())}")


