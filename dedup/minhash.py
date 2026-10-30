"""MinHash signatures and LSH banding for near-duplicate detection (NumPy, no external dedup libraries)."""
from __future__ import annotations

import hashlib
from collections import defaultdict

import numpy as np

from .normalise import normalise

MERSENNE = np.uint64((1 << 61) - 1)
MAX_HASH = np.uint64((1 << 32) - 1)


def shingles(text: str, k: int = 5) -> set[int]:
    """Word k-gram shingles, hashed to 32-bit integers."""
    words = normalise(text).split()
    if len(words) < k:
        words = words + [""] * (k - len(words))
    grams = {" ".join(words[i:i + k]) for i in range(len(words) - k + 1)}
    return {int.from_bytes(hashlib.blake2b(g.encode(), digest_size=4).digest(), "little") for g in grams}


class MinHasher:
    def __init__(self, num_perm: int = 128, seed: int = 1):
        rng = np.random.default_rng(seed)
        self.a = rng.integers(1, MERSENNE, size=num_perm, dtype=np.uint64)
        self.b = rng.integers(0, MERSENNE, size=num_perm, dtype=np.uint64)
        self.num_perm = num_perm

    def signature(self, shingle_set: set[int]) -> np.ndarray:
        x = np.fromiter(shingle_set, dtype=np.uint64)
        # (a*x + b) mod p, truncated to 32 bits; min over shingles for each permutation.
        hashed = ((np.outer(x, self.a) + self.b) % MERSENNE) & MAX_HASH
        return hashed.min(axis=0)


def estimated_jaccard(sig_a: np.ndarray, sig_b: np.ndarray) -> float:
    return float(np.mean(sig_a == sig_b))


def lsh_candidates(signatures: list[np.ndarray], bands: int = 32) -> set[tuple[int, int]]:
    """Pairs of documents that share at least one identical band of their signature."""
    rows = len(signatures[0]) // bands
    pairs: set[tuple[int, int]] = set()
    for band in range(bands):
        buckets: dict[bytes, list[int]] = defaultdict(list)
        for doc_id, sig in enumerate(signatures):
            buckets[sig[band * rows:(band + 1) * rows].tobytes()].append(doc_id)
        for ids in buckets.values():
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    pairs.add((ids[i], ids[j]))
    return pairs


def near_duplicate_groups(docs: list[str], threshold: float = 0.7, num_perm: int = 128,
                          bands: int = 32) -> list[list[int]]:
    """Cluster near-duplicates (estimated Jaccard >= threshold) with union-find. Returns groups of 2+ ids."""
    hasher = MinHasher(num_perm)
    sigs = [hasher.signature(shingles(d)) for d in docs]
    parent = list(range(len(docs)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, j in lsh_candidates(sigs, bands):
        if estimated_jaccard(sigs[i], sigs[j]) >= threshold:
            parent[find(j)] = find(i)
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(len(docs)):
        groups[find(i)].append(i)
    return [sorted(g) for g in groups.values() if len(g) > 1]
