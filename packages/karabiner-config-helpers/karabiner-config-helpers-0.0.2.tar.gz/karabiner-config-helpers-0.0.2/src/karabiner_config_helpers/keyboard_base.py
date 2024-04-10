from typing import Any
from enum import Enum

####### Convenience functions for better readability #############

def normal(key):
   return {"key_code": key}

def shift(key):
   return {"key_code": key, "modifiers": ["left_shift"]}

def option(key):
   return {"key_code": key, "modifiers": ["left_option"]}

def alt_gr(key):
   return {"key_code": key, "modifiers": ["right_option"]}

def shift_alt_gr(key):
   return {"key_code": key, "modifiers": ["left_shift","right_option"]}


######################### Basic classes ##########################3

class NoKeyMappingFoundError(Exception):
   def __init__(self, character: str) -> None:
      super().__init__(f"Can not type character '{character}' ({hex(ord(character))})")


class CharRequiresMultipleKeys(Exception):
   pass


class OperatingSystem(Enum):
    LINUX = 1
    MAC = 2
    WINDOWS = 3


class KeyResolver:
    """
    Resolve characters to the keystrokes that are required for them.
    Might return multiple keystrokes if that is required.
    If the key can not be typed a NoKeyMappingFoundError will be thrown.
    """

    def __init__(self, layout_name: str, os: OperatingSystem, *list_of_lookup_tables: dict) -> None:
        self.layout_name = layout_name
        self.os = os
        self._list_of_lookup_tables = list_of_lookup_tables

    def get_default_modifier_for_os(self) -> str:
        """
        Returns the default modifier for key bindings like copy, paste, select all, etc.
        Command on MacOS, Control on Linux and Windows
        """
        if self.os == OperatingSystem.MAC:
            return "command"
        elif self.os in [OperatingSystem.LINUX, OperatingSystem.WINDOWS]:
            return "control"
        else:
            raise Exception(f"Unknown operating system: {self.os}")

    def get_to_keys_for_char(self, character: str) -> list[dict[str,Any]]:
        """
        Maps a character to the keystrokes needed to type it. You can directly put the result into the "to" field of a manipulator.
        """
        if len(character) != 1:
            raise Exception(f"String '{character}' should have length 1")

        for mapping_table in self._list_of_lookup_tables:
            if mapping_value := mapping_table.get(character):
                return mapping_value if type(mapping_value) == list else [mapping_value]
  
        raise NoKeyMappingFoundError(character)

    def get_from_keys_for_char(self, character: str, extra_modifiers: list[str]) -> dict[str,Any]:
        """
        Maps a character to the key combo required to type it. The output can be directly put into the "from" field of a manipulator.
        If multiple key strokes are required a CharRequiresMultipleKeys exception will be thrown.
        """
        keys = self.get_to_keys_for_char(character)
        if len(keys) == 1:
            key = keys[0]
            key_code = key["key_code"]
            # Take original modifiers, generalize them, add extra_modifiers and then remove duplicates
            mandatory_modifiers = key.get("modifiers", [])
            mandatory_modifiers = [str(mod).replace("left_", "").replace("right_", "") for mod in mandatory_modifiers]
            mandatory_modifiers = list(set(mandatory_modifiers + extra_modifiers))

            return {
                "key_code": key_code,
                "modifiers": {
                    "mandatory": mandatory_modifiers,
                    "optional": [
                        "caps_lock"
                    ]
                }
            }
        else:
            raise CharRequiresMultipleKeys(character)


