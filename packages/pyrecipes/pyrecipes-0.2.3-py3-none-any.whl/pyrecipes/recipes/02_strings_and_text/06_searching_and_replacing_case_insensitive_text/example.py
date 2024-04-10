"""
You need to search for an possible replace text in a case-insensitive manner.
"""
import re


def matchcase(word: str):
    def replace(m):
        text = m.group()
        if text.isupper():
            return word.upper()
        elif text.islower():
            return word.lower()
        elif text[0].isupper():
            return word.capitalize()
        else:
            return word

    return replace


def main():
    text = "UPPER PYTHON, lower python, Mixed Python"
    print("text:", text)

    matches = re.findall("python", text, flags=re.IGNORECASE)
    print("matches:", matches)

    print("replace:", re.sub("python", "snake", text, flags=re.IGNORECASE))
    print(
        "replace (maintaining case):",
        re.sub("python", matchcase("snake"), text, flags=re.IGNORECASE),
    )


if __name__ == "__main__":
    main()
