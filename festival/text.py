
import re
import unicodedata
from festival.errors import InvalidValueError


def slugify(name: str) -> str:
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_text = decomposed.encode("ascii", "ignore").decode("ascii")
    lower = ascii_text.lower()
    with_dashes = re.sub(r"[^a-z0-9]+", "-", lower)
    return with_dashes.strip("-")
def clean_name(value: str, what: str) -> str:
    """Enlève les espaces autour d'un nom et refuse un nom vide."""
    cleaned = value.strip()
    if not cleaned:
        raise InvalidValueError(f"The {what} cannot be empty.")
    return cleaned