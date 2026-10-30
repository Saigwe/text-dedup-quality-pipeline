"""Exact deduplication on normalised content."""
import hashlib

from .normalise import normalise


def content_hash(text: str) -> str:
    return hashlib.sha256(normalise(text).encode("utf-8")).hexdigest()


def exact_dedup(docs: list[str]) -> tuple[list[str], list[int]]:
    """Return (kept documents, indices of removed duplicates), keeping the first occurrence."""
    seen, kept, removed = set(), [], []
    for i, doc in enumerate(docs):
        h = content_hash(doc)
        if h in seen:
            removed.append(i)
        else:
            seen.add(h)
            kept.append(doc)
    return kept, removed
