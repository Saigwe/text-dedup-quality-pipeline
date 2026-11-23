"""README chart from output/audit.md (written by the curation run).
Usage: python charts/make_charts.py [output/audit.md]"""
import re
import sys
from pathlib import Path

import style as st

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "output" / "audit.md"
OUT = ROOT / "docs" / "charts"

md = SRC.read_text(encoding="utf-8")
section = md.split("## Removals by reason", 1)[1].split("##", 1)[0]
rows = [(c[0], int(c[1].replace(",", ""))) for c in
        ([x.strip() for x in l.strip().strip("|").split("|")] for l in section.splitlines() if l.startswith("|"))
        if len(c) == 2 and c[1].replace(",", "").isdigit()]
before = int(re.search(r"\| Documents \| ([\d,]+) \| ([\d,]+) \|", md).group(1).replace(",", ""))
kept = int(re.search(r"\| Documents \| ([\d,]+) \| ([\d,]+) \|", md).group(2).replace(",", ""))
acc = re.search(r"Precision ([\d.]+)%, recall ([\d.]+)%", md)

NAMES = {"exact_duplicate": "Exact duplicate", "near_duplicate": "Near duplicate (MinHash)",
         "quality:low_alpha": "Quality: mostly numbers", "quality:symbol_heavy": "Quality: symbol-heavy",
         "quality:too_short": "Quality: too short", "quality:repetitive_lines": "Quality: repeated lines"}
labels = ["Kept"] + [NAMES.get(r[0], r[0]) for r in rows]
values = [kept] + [r[1] for r in rows]
colors = [st.S[2]] + [st.S[1] if "dup" in r[0] else st.S[3] for r in rows]
f, ax = st.fig(8, 3.4)
st.hbar(ax, labels, values, colors)
st.head(ax, f"{before - kept} of {before} documents removed, at {acc.group(1)}% precision and {acc.group(2)}% recall",
        "Where each document went; precision and recall measured against the planted labels", flush=True)
st.save(f, OUT / "curation_funnel.png")
print(f"wrote charts to {OUT}")
