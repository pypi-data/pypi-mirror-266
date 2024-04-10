import string
# local
from . import KeyResolver
from .keyboard_base import normal, shift, option, alt_gr, shift_alt_gr, OperatingSystem

KEYMAP_LETTERS_NUMBERS_UNMODIFIED = {}
for character in string.ascii_lowercase + string.digits:
    KEYMAP_LETTERS_NUMBERS_UNMODIFIED[character] = normal(character)
for character in string.ascii_uppercase:
    KEYMAP_LETTERS_NUMBERS_UNMODIFIED[character] = shift(character.lower())


KEYMAP_SPECIAL_US_LAYOUT = {
    # Whitespace
    "\n": normal("return_or_enter"),
    "\t": normal("tab"),
    " ": normal("spacebar"),

    # Top row
    "`": normal("grave_accent_and_tilde"),
    "~": shift("grave_accent_and_tilde"),
    "!": shift("1"),
    "@": shift("2"),
    "#": shift("3"),
    "$": shift("4"),
    "%": shift("5"),
    "^": shift("6"),
    "&": shift("7"),
    "*": shift("8"),
    "(": shift("9"),
    ")": shift("0"),
    "-": normal("hyphen"),
    "_": shift("hyphen"),
    "=": normal("equal_sign"),
    "+": shift("equal_sign"),

    # Upper row
    "[": normal("open_bracket"),
    "{": shift("open_bracket"),
    "]": normal("close_bracket"),
    "}": shift("close_bracket"),

    # Home row
    ";": normal("semicolon"),
    ":": shift("semicolon"),
    "'": normal("quote"),
    "\"": shift("quote"),
    "\\": normal("backslash"),
    "|": shift("backslash"),

    # Lower row
    ",": normal("comma"),
    "<": shift("comma"),
    ".": normal("period"),
    ">": shift("period"),
    "/": normal("slash"),
    "?": shift("slash"),

    # 0x0b - 0x0d missing (vertical tab, new page, carriage return), but who needs them anyways?
}

KEYMAP_MAC_UMLAUTS = {
    "ä": [option("u"), normal("a")],
    "Ä": [option("u"), shift("a")],
    "ö": [option("u"), normal("o")],
    "Ö": [option("u"), shift("o")],
    "ü": [option("u"), normal("u")],
    "Ü": [option("u"), shift("u")],
    "ß": option("s"),
}

KEYMAP_LINUX_US_DE_SE_FI_UMLAUTS = {
    # Umlauts for a linux with `setxkbmap -layout us -variant de_se_fi`
    "ä": alt_gr("a"),
    "Ä": shift_alt_gr("a"),
    "ö": alt_gr("o"),
    "Ö": shift_alt_gr("o"),
    "ü": alt_gr("u"),
    "Ü": shift_alt_gr("u"),
    "ß": alt_gr("s"),
}

RESOLVER_US_MAC = KeyResolver("US (Mac)", OperatingSystem.MAC, KEYMAP_LETTERS_NUMBERS_UNMODIFIED, KEYMAP_SPECIAL_US_LAYOUT, KEYMAP_MAC_UMLAUTS)
RESOLVER_US_LINUX = KeyResolver("US (Linux, de_se_fi)", OperatingSystem.LINUX, KEYMAP_LETTERS_NUMBERS_UNMODIFIED, KEYMAP_SPECIAL_US_LAYOUT, KEYMAP_LINUX_US_DE_SE_FI_UMLAUTS)

