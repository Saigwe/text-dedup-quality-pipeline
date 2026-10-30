# 3-minute walkthrough: Text Dedup & Quality Pipeline

A timed script for a Loom recording of about 3 minutes (screen plus camera bubble, 1080p). Say it in your own words; the lines are a guide, not a teleprompter.

**Open these tabs before you press record:** README, the pipeline diagram, `dedup/exact.py`, `dedup/minhash.py`, `dedup/filters.py`, `output/audit.md`, GitHub Actions.

| Time | On screen | What to say |
|---|---|---|
| 0:00–0:20 | Portfolio card, then the README title | Duplicate and junk text in AI training data wastes compute and skews models. This pipeline removes it, explains every removal, and is scored against labels. |
| 0:20–0:40 | README intro and the pipeline diagram | The corpus is synthetic and labelled: 550 documents, with exact copies, near-copies and junk planted. Preparing data for AI and ML is part of my day job; here the curation is measured, not eyeballed. |
| 0:40–1:05 | `dedup/exact.py` | Cheapest checks first: a SHA-256 of normalised text removes exact copies before anything expensive runs. |
| 1:05–1:35 | `dedup/minhash.py` | Near-duplicates use MinHash on word 5-gram shingles, written from scratch in NumPy, with 32 LSH bands of 4 rows. Only documents that share a band are compared, never all pairs. |
| 1:35–2:05 | `dedup/filters.py` | Then heuristic quality filters: length, symbols, repeated lines, alphabetic and stopword ratios. Every removal carries a reason code. |
| 2:05–2:30 | Results table, then `output/audit.md` | It keeps 405 of 550 documents, with 100% precision and 96.7% recall on removals. The audit shows removals by reason, with an example of each. |
| 2:30–2:45 | README: threshold trade-off | The 5 misses are near-copies under the 0.7 similarity threshold. Lowering it would catch them but risks merging distinct documents that share boilerplate, and that's the decision I'd defend. |
| 2:45–3:00 | Back to the README top | Next is a public corpus and a PySpark port for scale. For an AI team, it's training data you can audit. Links are under the video. |

## Recording checklist
- Close email, chat and notifications. Zoom the browser to 125% so code is readable.
- Run `python -m dedup.audit` once before recording so the audit is fresh.
- Keep to one take per section; Loom lets you trim. Aim for 2:45 to 3:10.
- Show real numbers on screen as you say them; never estimate on camera.
- Say "synthetic" out loud when you introduce the data. This is a skills demonstration, not a rebuild of client work.

## After recording
1. Copy the Loom share link.
2. In `README.md`, replace the walkthrough line with `- [x] [3-minute Loom walkthrough](<your Loom link>)` and add the link under the title.
3. Add the link to this project's card on saigwe.github.io.
