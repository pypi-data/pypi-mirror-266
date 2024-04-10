from typing import Dict, List, Optional, TextIO
import re

_TEXT_COLOR_MAPPING = {
    "blue": "36;1",
    "yellow": "33;1",
    "pink": "38;5;200",
    "green": "32;1",
    "red": "31;1",
}

def get_colored_text(text: str, color: str) -> str:
    """Get colored text."""
    color_str = _TEXT_COLOR_MAPPING[color]
    return f"\u001b[{color_str}m\033[1;3m{text}\u001b[0m"

def remove_escape_codes(text):
    escape_pattern = re.compile(r'\x1b[^m]*m')
    return escape_pattern.sub('', text)

def remove_space(text):
    clean_text = text.strip().replace("\n", " ")
    clean_text = clean_text + "\n"
    return clean_text

def print_text(
    text: str, color: Optional[str] = None, end: str = "", file: Optional[TextIO] = None
) -> None:
    """Print text with highlighting and no end characters."""

    text_to_print = get_colored_text(text, color) if color else text
    text_to_print = remove_escape_codes(text_to_print)
    text_to_print = remove_space(text_to_print)

    print(text_to_print, end=end, file=file)
    if file:
        file.flush()  # ensure all printed content are written to file
