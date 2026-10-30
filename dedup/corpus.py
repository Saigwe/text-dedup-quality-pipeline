"""Synthetic labelled corpus: clean documents, exact and near duplicates, and junk.

Labels let the pipeline be scored for precision and recall instead of eyeballed.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

TOPICS = ["river", "harbour", "library", "orchard", "railway", "market", "bridge", "festival", "museum", "valley"]
VERBS = ["connects", "supports", "shapes", "attracts", "protects", "feeds", "records", "celebrates"]
NOUNS = ["families", "traders", "students", "farmers", "visitors", "engineers", "historians", "musicians"]
ADJ = ["old", "busy", "quiet", "famous", "modern", "remote", "seasonal", "local"]


def sentence(rng: random.Random, topic: str) -> str:
    return (f"The {rng.choice(ADJ)} {topic} {rng.choice(VERBS)} {rng.choice(NOUNS)} in the region, and it is "
            f"known for its {rng.choice(ADJ)} history with {rng.choice(NOUNS)} and {rng.choice(NOUNS)}.")


def clean_doc(rng: random.Random) -> str:
    topic = rng.choice(TOPICS)
    return " ".join(sentence(rng, topic) for _ in range(rng.randint(5, 9)))


def near_copy(rng: random.Random, doc: str, edits: int = 3) -> str:
    words = doc.split()
    for _ in range(edits):
        words[rng.randrange(len(words))] = rng.choice(ADJ + NOUNS)
    return " ".join(words)


def junk(rng: random.Random) -> tuple[str, str]:
    kind = rng.choice(["too_short", "symbol_heavy", "repetitive_lines", "low_alpha"])
    if kind == "too_short":
        return "Click here to subscribe to our newsletter today.", kind
    if kind == "symbol_heavy":
        return " ".join(rng.choice(["$$$", "###", ">>>", "@@", "%%%", "free", "win", "&&&"]) for _ in range(60)), kind
    if kind == "repetitive_lines":
        return "\n".join(["Home | About | Contact | Login"] * 12 + ["Copyright 2026 All rights reserved."]), kind
    return " ".join(str(rng.randint(1000, 99999)) for _ in range(60)), kind


def generate(n_clean: int = 400, seed: int = 5) -> list[dict]:
    """Return records with text and a ground-truth label: clean | exact_dup | near_dup | junk:<reason>."""
    rng = random.Random(seed)
    records, originals = [], []
    for src in range(n_clean):
        doc = clean_doc(rng)
        originals.append(doc)
        records.append({"text": doc, "label": "clean", "source_id": src})
    for src in rng.sample(range(n_clean), 40):
        records.append({"text": "  " + originals[src].upper().replace(". ", ".   "), "label": "exact_dup",
                        "source_id": src})
    for src in rng.sample(range(n_clean), 60):
        records.append({"text": near_copy(rng, originals[src]), "label": "near_dup", "source_id": src})
    for _ in range(50):
        text, reason = junk(rng)
        records.append({"text": text, "label": f"junk:{reason}", "source_id": None})
    rng.shuffle(records)
    for i, r in enumerate(records):
        r["id"] = i
    return records


def write_jsonl(records: list[dict], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
    return path


def read_jsonl(path: str | Path, text_field: str = "text") -> list[dict]:
    out = []
    for i, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines()):
        if line.strip():
            rec = json.loads(line)
            out.append({"id": rec.get("id", i), "text": rec[text_field], "label": rec.get("label"),
                        "source_id": rec.get("source_id")})
    return out
