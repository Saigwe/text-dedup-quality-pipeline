"""Heuristic quality filters. Each returns a reason code when a document should be removed, else None."""
from __future__ import annotations

import re

STOPWORDS = {"the", "and", "of", "to", "a", "in", "is", "that", "for", "it", "on", "with", "as", "was", "are"}

MIN_WORDS = 30
MAX_SYMBOL_RATIO = 0.10
MAX_REPEATED_LINE_RATIO = 0.30
MIN_STOPWORD_RATIO = 0.08
MIN_ALPHA_RATIO = 0.70


def too_short(text: str) -> str | None:
    return "too_short" if len(text.split()) < MIN_WORDS else None


def symbol_heavy(text: str) -> str | None:
    symbols = sum(1 for c in text if not (c.isalnum() or c.isspace() or c in ".,;:'\"!?()-"))
    return "symbol_heavy" if symbols / max(len(text), 1) > MAX_SYMBOL_RATIO else None


def repetitive_lines(text: str) -> str | None:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) < 3:
        return None
    repeated = len(lines) - len(set(lines))
    return "repetitive_lines" if repeated / len(lines) > MAX_REPEATED_LINE_RATIO else None


def low_alpha(text: str) -> str | None:
    tokens = text.split()
    alpha = sum(1 for t in tokens if re.fullmatch(r"[A-Za-z][A-Za-z'\-]*[.,;:!?]?", t))
    return "low_alpha" if alpha / max(len(tokens), 1) < MIN_ALPHA_RATIO else None


def not_english_prose(text: str) -> str | None:
    words = re.findall(r"[a-z']+", text.lower())
    ratio = sum(1 for w in words if w in STOPWORDS) / max(len(words), 1)
    return "not_english_prose" if ratio < MIN_STOPWORD_RATIO else None


FILTERS = [too_short, symbol_heavy, repetitive_lines, low_alpha, not_english_prose]


def first_failure(text: str) -> str | None:
    for f in FILTERS:
        reason = f(text)
        if reason:
            return reason
    return None
