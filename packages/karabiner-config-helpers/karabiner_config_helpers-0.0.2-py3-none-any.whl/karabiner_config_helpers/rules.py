#!/usr/bin/env python3
import json
import re
import os
from typing import Optional, Any
# local
from . import KarabinerConfigFileError

# General expected rule description:
# [PRIORITY] [#NAME] [DESCRIPTION]
# PRIORITY needs to be at the beginning of the line, the rest is your choice. You can also insert separators between elements to make them visually stand out. Example:
# "+50 | #MOD-FN | fn -> left_control"

# PRIORITY controls in which order rules are executed
# NAME can be used to identify rules to replace/delete (so that changing the description or priority will not make it unrecognizable)
# DESCRIPTION is your description of the rule

PRIORITY_REGEX = re.compile("^([+-]?[0-9]+)[\s$]")
NAME_REGEX = re.compile("[\s^](#\S+)[\s$]")

# Taken from https://karabiner-elements.pqrs.org/docs/json/location/
CONFIG_PATH = os.path.expanduser("~/.config/karabiner/karabiner.json")

DEFAULT_PROFILE = "Default profile"


def get_rule_priority_from_description(rule_json: dict) -> int:
    # Priority at the beginning of the line looks like '+5 | Your description' or '-10 | This will be run late'
    # If no priority is given, 0 will be assumed. Higher priority -> executed earlier
    description = rule_json.get("description", "")
    if match := PRIORITY_REGEX.match(description):
        priority_str = match.group(1)
        return int(priority_str, 10)
    else:
        return 0


def get_rule_name_from_description(rule_json: dict) -> Optional[str]:
    description = rule_json.get("description", "")
    if match := NAME_REGEX.search(description):
        return match.group(1)
    else:
        return None


def get_rules_of_profile(config_json: dict, target_profile: str) -> list[dict]:
    profile_list = config_json.get("profiles")
    if profile_list:
        for index, profile in enumerate(profile_list):
            name = profile.get("name")
            if name:
                if name == target_profile:
                    result = profile.get("complex_modifications", {}).get("rules")
                    if type(result) == list:
                        return result
                    else:
                        raise KarabinerConfigFileError(f"Expected a list as value of 'profiles[{index}].complex_modifications.rules' in karabiner configuration file")
            else:
                raise KarabinerConfigFileError(f"Expected non-empty key 'profiles[{index}].name' in karabiner configuration file")

        raise KarabinerConfigFileError(f"Found not profile with the name '{target_profile}' in karabiner configuration file")
    else:
        raise KarabinerConfigFileError("Expected non-empty key 'profiles' in karabiner configuration file")


def debug_main(config_json: dict, target_profile: str) -> None:
    for rule_json in get_rules_of_profile(config_json, target_profile):
        description = rule_json.get("description", "")
        print("\n", f'"{description}"')
        prio = get_rule_priority_from_description(rule_json)
        name = get_rule_name_from_description(rule_json)
        prio and print(f"  -> Prio: {prio}")
        name and print(f"  -> Name: {name}")


def stable_sort_rules_by_priority(rule_json_list: list[dict]) -> list[dict]:
    # We negate the weight, since high priority (bigger numbers) should be earlier.
    # We use the index to guarantee that the sorting is stable
    rules_with_weights = [(-get_rule_priority_from_description(rule_json), index, rule_json) for index, rule_json in enumerate(rule_json_list)]
    rules_with_weights.sort()
    return [rule_json for _, _, rule_json in rules_with_weights]


def sort_rules(config_json: dict, target_profile: str) -> None:
    # Lets try it this way, so that we do not need to implement the error handling twice:
    rules = get_rules_of_profile(config_json, target_profile)
    sorted_rules = stable_sort_rules_by_priority(rules)
    rules[:] = sorted_rules

    # for profile in config_json["profiles"]:
    #     if profile["name"] == target_profile:
    #         unsorted_rules = profile["complex_modifications"]["rules"]
    #         sorted_rules = stable_sort_rules_by_priority(unsorted_rules)
    #         profile["complex_modifications"]["rules"] = sorted_rules
    #         return


def replace_or_insert_rule(config_json: dict, target_profile: str, new_rule_json: dict) -> None:
    new_name = get_rule_name_from_description(new_rule_json)
    # IMPORTANT CHECK: If you remove it, all rules without names will be removed if you add a rule without a name :/
    if new_name:
        delete_rule_by_name(config_json, target_profile, new_name)
    else:
        description = str(new_rule_json.get("description", ""))
        print("[W] Warning: Please do not add a rule without a name (#SOME_NAME), otherwise replacing it will not work properly")
        # Prevent a situation where a rule without description causes unexpected deletions
        if description:
            delete_rule_by_description(config_json, target_profile, description)

    # Default to adding it after rules of the same priority
    get_rules_of_profile(config_json, target_profile).append(new_rule_json)
    sort_rules(config_json, target_profile)


def delete_rule_by_name(config_json: dict, target_profile: str, target_name: str):
    rules = get_rules_of_profile(config_json, target_profile)
    print(f"Found {len(rules)} rule(s)")

    for rule_index in range(len(rules)-1, 0, -1):
        if get_rule_name_from_description(rules[rule_index]) == target_name:
            print(f"Deleting rule at index {rule_index}")
            del rules[rule_index]


def delete_rule_by_description(config_json: dict, target_profile: str, target_description: str):
    rules = get_rules_of_profile(config_json, target_profile)
    print(f"Found {len(rules)} rule(s)")

    for rule_index in range(len(rules)-1, -1, -1):
        if rules[rule_index].get("description", "") == target_description:
            print(f"Deleting rule at index {rule_index}")
            del rules[rule_index]


def load_config(path: str) -> dict[str,Any]:
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as ex:
        raise Exception(f"Failed to load JSON file '{path}':", ex)


def store_config(config: dict[str,Any]) -> None:
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as ex:
        raise Exception("Failed to store settings:", ex)


def helper_insert_rule_into_config(rule_to_insert: dict, target_profile: str = DEFAULT_PROFILE):
    config = load_config(CONFIG_PATH)
    replace_or_insert_rule(config, target_profile, rule_to_insert)
    store_config(config)

