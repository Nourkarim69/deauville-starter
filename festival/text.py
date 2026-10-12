
import re
import unicodedata


def slugify(name: str) -> str:
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_text = decomposed.encode("ascii", "ignore").decode("ascii")
    lower = ascii_text.lower()
    with_dashes = re.sub(r"[^a-z0-9]+", "-", lower)
    return with_dashes.strip("-")