import json
import os
# local
from . import get_resolver, NoResolverWithName

# Different applications can have different layouts (like a Windows VM in Parallels) or a RDP client or a web browser with Guacamole.
# So that we do not need to handle these cases in every single function and reimplement the handling, we add these helpers

APP_CONFIG_PATH = os.path.expanduser("~/.config/karabiner/app_resolvers.json")


class AppResolverMap:
    def __init__(self, default_resolver_name: str):
        self._map: dict[str,list[str]] = {}
        self.default_resolver_name = default_resolver_name

    def add_application(self, app_bundle_id_regex: str, keyboard_layout: str) -> None:
        try:
            get_resolver(keyboard_layout)
        except NoResolverWithName:
            raise NoResolverWithName(f"Application '{app_bundle_id_regex}' references the non-existent resolver / keyboard layout '{keyboard_layout}'")
        
        # @TODO: check for duplicates (especially with different ids)?
        # Store the mapping of layout and bundle id
        try:
            self._map[keyboard_layout].append(app_bundle_id_regex)
        except KeyError:
            self._map[keyboard_layout] = [app_bundle_id_regex]

    def get_resolver_names_and_conditions(self) -> list[tuple[str, list[dict]]]:
        return convert_bundle_id_dict_to_conditions(self._map, self.default_resolver_name)

    def get_default_modifier_keys_and_conditions(self) -> list[tuple[str, list[dict]]]:
        default_default_modifier = get_resolver(self.default_resolver_name).get_default_modifier_for_os()
        modifiers_to_bundle_ids = {}

        for resolver_name, bundle_id_regexes in self._map.items():
            resolver_default_modifier = get_resolver(resolver_name).get_default_modifier_for_os()
            # first handle the exceptions, then later the general cause
            if resolver_default_modifier != default_default_modifier:
                # remember all exceptions for the default clause
                modifiers_to_bundle_ids[resolver_default_modifier] = modifiers_to_bundle_ids.get(resolver_default_modifier, []) + bundle_id_regexes
                
        return convert_bundle_id_dict_to_conditions(modifiers_to_bundle_ids, default_default_modifier)


def convert_bundle_id_dict_to_conditions(dict_mapping_to_bundle_ids: dict[str,list[str]], default_value: str) -> list[tuple[str, list[dict]]]:
    """
    We return a list of conditions instead of a string or None, since this is easier to handle by the calling function
    """
    if dict_mapping_to_bundle_ids:
        results = []

        # Handle the exceptions
        non_default_bundle_id_regexes: list[str] = []
        for key, bundle_id_regexes in dict_mapping_to_bundle_ids.items():
            condition = {
                "type": "frontmost_application_if",
                "bundle_identifiers": bundle_id_regexes,
            }
            results.append((key, [condition]))
            non_default_bundle_id_regexes += bundle_id_regexes

        # Handle the default clause
        condition = {
            "type": "frontmost_application_unless",
            "bundle_identifiers": non_default_bundle_id_regexes,
        }
        results.append((default_value, [condition]))
        return results
    else:
        # Special case: no exceptions
        return [(default_value, [])]



def load_app_resolver_map_json():
    """
    Example config file:
    {
        "default": "us_mac",
        "^com\\.parallels\\.desktop\\.console$": "us_linux",
        "^com\\.apple\\.Safari$": "us_linux"
    }
    """
    if os.path.exists(APP_CONFIG_PATH):
        # Load the data from the users configuration file
        with open(APP_CONFIG_PATH) as f:
            data = json.load(f)


        result = AppResolverMap(data.get("default", "us_mac"))
        for bundle_id_regex, resolver_name in data.items():
            if bundle_id_regex != "default":
                result.add_application(bundle_id_regex, resolver_name)

        return result            
    else:
        # No configuration file exists, so we attempt to create some sane defaults for me:

        # Most applications are on the host -> use host layout
        result = AppResolverMap("us_mac")

        # Parallels likely has linux (and sometimes Windows) VMs in it
        result.add_application(r"^com\.parallels\.desktop\.console$", "us_linux")

        # I use Safari for stuff like Guacamole
        result.add_application(r"^com\.apple\.Safari$", "us_linux")

        return result
