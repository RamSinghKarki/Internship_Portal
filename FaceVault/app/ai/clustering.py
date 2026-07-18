"""Face clustering and identity assignment.

Two-stage, incremental by design (a full re-cluster of a million faces on
every scan does not scale):

  1. MATCH: each new face is compared against existing person centroids;
     a hit above the threshold joins that person.
  2. CLUSTER: leftover faces are grouped among themselves with
     agglomerative single-link clustering (union-find over pairwise cosine
     similarity). Clusters reaching min_cluster_size become new persons;
     the rest stay in the "unknown" pool for a future scan to claim.

The pairwise step is O(n²) in *new unassigned* faces only, which stays
small per scan. Swap in FAISS + HDBSCAN behind this same interface when a
library outgrows it (see docs/ARCHITECTURE.md).
"""

from dataclasses import dataclass

import numpy as np


class _UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, i: int) -> int:
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


@dataclass
class ClusterResult:
    # face_id -> existing person_id
    matched: dict[int, int]
    # each inner list is a set of face_ids forming a NEW person
    new_clusters: list[list[int]]
    # face_ids that stay unassigned
    leftover: list[int]


def cluster_faces(
    face_ids: list[int],
    embeddings: np.ndarray,
    person_centroids: dict[int, np.ndarray],
    match_threshold: float,
    min_cluster_size: int = 2,
    match_margin: float = 0.0,
) -> ClusterResult:
    """Assign new faces to existing persons, then cluster the remainder.

    `embeddings` must be L2-normalized, shape (n, dim), aligned with face_ids.
    `match_margin` guards against look-alikes: a face is assigned only when
    its best person beats the runner-up by at least this much; ambiguous
    faces stay unassigned for human review rather than being guessed.
    """
    matched: dict[int, int] = {}
    ambiguous_idx: list[int] = []
    remaining_idx: list[int] = []

    if person_centroids and len(face_ids):
        pids = list(person_centroids.keys())
        cmat = np.stack([person_centroids[p] for p in pids])  # (P, dim)
        sims = embeddings @ cmat.T  # (n, P)
        for i in range(len(face_ids)):
            order = np.argsort(-sims[i])
            best_sim = sims[i, order[0]]
            second_sim = sims[i, order[1]] if len(pids) > 1 else -1.0
            if best_sim < match_threshold:
                remaining_idx.append(i)
            elif best_sim - second_sim < match_margin:
                ambiguous_idx.append(i)  # two people match: don't guess
            else:
                matched[face_ids[i]] = pids[order[0]]
    else:
        remaining_idx = list(range(len(face_ids)))

    new_clusters: list[list[int]] = []
    leftover: list[int] = []

    if remaining_idx:
        sub = embeddings[remaining_idx]
        n = len(remaining_idx)
        uf = _UnionFind(n)
        sims = sub @ sub.T
        for i in range(n):
            for j in range(i + 1, n):
                if sims[i, j] >= match_threshold:
                    uf.union(i, j)

        buckets: dict[int, list[int]] = {}
        for i in range(n):
            buckets.setdefault(uf.find(i), []).append(i)

        for members in buckets.values():
            ids = [face_ids[remaining_idx[m]] for m in members]
            if len(ids) >= min_cluster_size:
                new_clusters.append(ids)
            else:
                leftover.extend(ids)

    # Ambiguous faces never form new persons — they wait for manual review.
    leftover.extend(face_ids[i] for i in ambiguous_idx)

    return ClusterResult(matched=matched, new_clusters=new_clusters, leftover=leftover)


def centroid(embeddings: np.ndarray) -> np.ndarray:
    """Normalized mean of normalized embeddings."""
    m = embeddings.mean(axis=0)
    n = np.linalg.norm(m)
    return m / n if n > 0 else m
