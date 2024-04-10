from argparse import ArgumentParser
import sys
from typing import Callable, Any
# local
from .rules import helper_insert_rule_into_config

def print_json(full_json: dict) -> None:
    import json
    # Print the config to the standard output stream
    json.dump(full_json, sys.stdout, indent=4)


def helper_default_argument_parser_action_handler(ap: ArgumentParser, function_generate_config_json: Callable[[Any],dict]) -> None:
    """
    function_generate_config_json is a function accepting the parsed arguments and returns the dict (JSON like object) of the rule generated
    """
    ap.add_argument("--print", action="store_true", help="instead of inserting the rule just print it to stdout")
    args = ap.parse_args()

    full_json = function_generate_config_json(args)    
    if args.print:
        print_json(full_json)
    else:
        try:
            # Insert the rule directly into the config
            helper_insert_rule_into_config(full_json)
        except Exception as ex:
            # If the insertion failed, we print it to the console as a fallback.
            print("[-] Failed to insert rule into config because of error:", ex, file=sys.stderr)
            print_json(full_json)
