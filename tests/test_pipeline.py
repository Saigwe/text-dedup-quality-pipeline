from dedup.audit import curate, score
from dedup.corpus import clean_doc, generate, near_copy
from dedup.filters import first_failure
from dedup.minhash import MinHasher, estimated_jaccard, near_duplicate_groups, shingles

import random


def test_minhash_estimates_similarity():
    rng = random.Random(1)
    doc = clean_doc(rng)
    other = clean_doc(rng)
    h = MinHasher()
    same = estimated_jaccard(h.signature(shingles(doc)), h.signature(shingles(near_copy(rng, doc, 1))))
    diff = estimated_jaccard(h.signature(shingles(doc)), h.signature(shingles(other)))
    assert same > 0.7
    assert diff < 0.3


def test_near_duplicate_groups_cluster_copies():
    rng = random.Random(2)
    a, b = clean_doc(rng), clean_doc(rng)
    groups = near_duplicate_groups([a, b, near_copy(rng, a, 2)])
    assert groups == [[0, 2]]


def test_filters_give_reason_codes():
    assert first_failure("too few words here") == "too_short"
    assert first_failure(" ".join(["$$$ ###"] * 40)) == "symbol_heavy"
    assert first_failure("\n".join(["Home | About | Contact"] * 10 + ["the and of to a in is that for it " * 4])) \
        == "repetitive_lines"
    assert first_failure(clean_doc(random.Random(3))) is None


def test_pipeline_precision_and_recall_on_labelled_corpus():
    records = generate()
    kept, removed = curate(records)
    metrics = score(records, removed)
    assert metrics["precision"] >= 0.95
    assert metrics["recall"] >= 0.9
    assert all(r["label"] == "clean" for r in kept) or len(kept) > 350
