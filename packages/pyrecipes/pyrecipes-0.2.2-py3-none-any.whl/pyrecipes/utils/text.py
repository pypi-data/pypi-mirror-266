import re


def clean_text(text):
    num, text = text.split("_", maxsplit=1)
    return f"{int(num)}) {text.replace('_', ' ').capitalize()}"


def extract_leading_numbers(text):
    m = re.match(r"^\d+", text)
    if m:
        return int(m.group())


def text_border(text, symbol="=", side_symbol="=", padding=1):
    width = 2 * padding + len(text) + 2
    top = bottom = f"{symbol * width}"
    pad = " " * padding
    return f"{top}\n{side_symbol}{pad}{text}{pad}{side_symbol}\n{bottom}"
