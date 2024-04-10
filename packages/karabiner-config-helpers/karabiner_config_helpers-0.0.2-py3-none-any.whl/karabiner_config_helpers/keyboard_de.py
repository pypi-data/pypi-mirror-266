import string
# local
from . import KeyResolver
from .keyboard_us import KEYMAP_LETTERS_NUMBERS_UNMODIFIED
from .keyboard_base import normal, shift, option, alt_gr, shift_alt_gr, OperatingSystem


KEYMAP_LETTERS_SWAP_Y_Z = {
    "z": normal("y"),
    "Z": shift("Y"),
    "y": normal("z"),
    "Y": shift("Z"),
}

KEYMAP_SPECIAL_DE_LAYOUT = {
    # Whitespace
    "\n": normal("return_or_enter"),
    "\t": normal("tab"),
    " ": normal("spacebar"),

    # Top row
    "^": normal("grave_accent_and_tilde"),
    # "": shift("grave_accent_and_tilde"), Yourd round accent
    "!": shift("1"),
    "\"": shift("2"),
    "§": shift("3"),
    "$": shift("4"),
    "%": shift("5"),
    "^": shift("6"),
    "/": shift("7"),
    "(": shift("8"),
    ")": shift("9"),
    "=": shift("0"),
    "ß": normal("hyphen"),
    "?": shift("hyphen"),
    # "": normal("equal_sign"), Weird accent
    "`": shift("equal_sign"),

    # Top row (AltGr)
    "{": alt_gr("7"),
    "[": alt_gr("8"),
    "]": alt_gr("9"),
    "}": alt_gr("0"),

    # Upper row
    "@": alt_gr("Q"),
    "ü": normal("open_bracket"),
    "Ü": shift("open_bracket"),
    "+": normal("close_bracket"),
    "*": shift("close_bracket"),
    "~": alt_gr("close_bracket"),
    "#": normal("backslash"),
    "'": shift("backslash"),

    # Home row
    "ö": normal("semicolon"),
    "Ö": shift("semicolon"),
    "ä": normal("quote"),
    "Ä": shift("quote"),

    # Lower row
    ",": normal("comma"),
    ";": shift("comma"),
    ".": normal("period"),
    ":": shift("period"),
    "-": normal("slash"),
    "_": shift("slash"),
    # This is a guess @TODO: check code
    "<": normal("non_us_backslash"),
    ">": shift("non_us_backslash"),
    "|": alt_gr("non_us_backslash"),

    # 0x0b - 0x0d missing (vertical tab, new page, carriage return), but who needs them anyways?
}


RESOLVER_DE_LINUX = KeyResolver("DE (Linux)", OperatingSystem.LINUX, KEYMAP_LETTERS_SWAP_Y_Z, KEYMAP_LETTERS_NUMBERS_UNMODIFIED, KEYMAP_SPECIAL_DE_LAYOUT)

