"""Run the curation pipeline and write an audit: python -m dedup.audit [--input corpus.jsonl]

Order: exact dedup -> near dedup -> quality filters. Every removed document keeps a reason code.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from .corpus import generate, read_jsonl, write_jsonl
from .exact import content_hash
from .filters import first_failure
from .minhash import near_duplicate_groups

ROOT = Path(__file__).resolve().parent.parent


def curate(records: list[dict], threshold: float = 0.7) -> tuple[list[dict], dict[int, str]]:
    """Return (kept records, removed id -> reason)."""
    removed: dict[int, str] = {}
    seen: set[str] = set()
    for r in records:
        h = content_hash(r["text"])
        if h in seen:
            removed[r["id"]] = "exact_duplicate"
        seen.add(h)

    remaining = [r for r in records if r["id"] not in removed]
    for group in near_duplicate_groups([r["text"] for r in remaining], threshold):
        for idx in group[1:]:  # keep the first document in each cluster
            removed[remaining[idx]["id"]] = "near_duplicate"

    for r in records:
        if r["id"] not in removed:
            reason = first_failure(r["text"])
            if reason:
                removed[r["id"]] = f"quality:{reason}"
    kept = [r for r in records if r["id"] not in removed]
    return kept, removed


def score(records: list[dict], removed: dict[int, str]) -> dict[str, float]:
    """Precision/recall of removals against labels.

    Junk should always be removed. For each source document and its copies, exactly one member should be kept,
    and it does not matter which one. So a removal is correct if the record is junk, or another member of its
    source group survived.
    """
    groups: dict[int, list[int]] = {}
    for r in records:
        if r.get("source_id") is not None:
            groups.setdefault(r["source_id"], []).append(r["id"])
    junk = {r["id"] for r in records if r["label"].startswith("junk")}
    should_remove = len(junk) + sum(len(g) - 1 for g in groups.values())

    by_id = {r["id"]: r for r in records}
    correct = 0
    for i in removed:
        src = by_id[i].get("source_id")
        if i in junk or (src is not None and any(m not in removed for m in groups[src] if m != i)):
            correct += 1
    precision = correct / max(len(removed), 1)
    recall = correct / max(should_remove, 1)
    return {"precision": round(precision, 3), "recall": round(recall, 3),
            "removed": len(removed), "should_remove": should_remove}


def word_stats(records: list[dict]) -> dict[str, float]:
    lengths = sorted(len(r["text"].split()) for r in records)
    return {"documents": len(lengths), "median_words": lengths[len(lengths) // 2],
            "total_words": sum(lengths)}


def write_report(records, kept, removed, metrics, out: Path) -> str:
    reasons = Counter(removed.values())
    before, after = word_stats(records), word_stats(kept)
    by_id = {r["id"]: r for r in records}
    samples = "\n".join(
        f"- `{reason}`: {by_id[i]['text'][:110].replace(chr(10), ' ')}..."
        for reason in sorted(reasons) for i in [next(k for k, v in removed.items() if v == reason)]
    )
    report = f"""# Curation audit

| | Before | After |
|---|---|---|
| Documents | {before['documents']} | {after['documents']} |
| Total words | {before['total_words']:,} | {after['total_words']:,} |
| Median words per document | {before['median_words']} | {after['median_words']} |

## Removals by reason

| Reason | Documents |
|---|---|
""" + "\n".join(f"| {k} | {v} |" for k, v in reasons.most_common()) + f"""

## Accuracy against labels

Precision {metrics['precision']:.1%}, recall {metrics['recall']:.1%} ({metrics['removed']} removed,
{metrics['should_remove']} labelled for removal).

## One example per reason

{samples}
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSONL corpus with a 'text' field (default: synthetic labelled corpus)")
    parser.add_argument("--threshold", type=float, default=0.7)
    args = parser.parse_args()
    if args.input:
        records = read_jsonl(args.input)
    else:
        records = generate()
        write_jsonl(records, ROOT / "data" / "synthetic_corpus.jsonl")
    kept, removed = curate(records, args.threshold)
    metrics = score(records, removed) if all(r.get("label") for r in records) else {}
    write_report(records, kept, removed, metrics or {"precision": 0, "recall": 0, "removed": len(removed),
                                                      "should_remove": 0}, ROOT / "output" / "audit.md")
    write_jsonl(kept, ROOT / "output" / "curated.jsonl")
    print(f"kept {len(kept)} of {len(records)} documents; {metrics}")


if __name__ == "__main__":
    main()
