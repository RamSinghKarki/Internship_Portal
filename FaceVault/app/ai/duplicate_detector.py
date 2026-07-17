"""Near-duplicate grouping over perceptual hashes.

Exact duplicates are a pure SQL GROUP BY on sha256 (see Repository);
this module handles the fuzzy case: resized, re-encoded or lightly
edited copies whose dHashes differ by a few bits.

O(n²) comparisons — fine up to tens of thousands of images. A BK-tree
or multi-index hashing slots in here for larger libraries.
"""

from ..utils.hashing import hamming


def near_duplicate_groups(
    items: list[tuple[int, int]], max_distance: int = 5
) -> list[list[int]]:
    """Group image ids whose 64-bit dHashes are within max_distance bits.

    items: list of (image_id, dhash_int). Returns groups of 2+ ids.
    """
    n = len(items)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(n):
        for j in range(i + 1, n):
            if hamming(items[i][1], items[j][1]) <= max_distance:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[rj] = ri

    buckets: dict[int, list[int]] = {}
    for i in range(n):
        buckets.setdefault(find(i), []).append(items[i][0])
    return [ids for ids in buckets.values() if len(ids) > 1]
