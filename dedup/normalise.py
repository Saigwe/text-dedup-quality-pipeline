"""Text normalisation used before hashing."""
import re
import unicodedata


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"\s+", " ", text).strip()
