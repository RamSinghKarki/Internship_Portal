import numpy as np

from app.ai.clustering import centroid, cluster_faces


def _norm(v):
    return v / np.linalg.norm(v)


def _synthetic_person(base_seed: int, n: int, dim: int = 128, noise: float = 0.06):
    """n noisy variants of one random unit vector = one 'person'."""
    rng = np.random.default_rng(base_seed)
    base = _norm(rng.normal(size=dim))
    return [_norm(base + rng.normal(scale=noise, size=dim)) for _ in range(n)]


def test_new_clusters_formed_per_person():
    a = _synthetic_person(1, 4)
    b = _synthetic_person(2, 3)
    embs = np.stack(a + b)
    ids = list(range(7))

    result = cluster_faces(ids, embs, {}, match_threshold=0.5, min_cluster_size=2)

    assert not result.matched
    assert sorted(len(c) for c in result.new_clusters) == [3, 4]
    groups = [set(c) for c in result.new_clusters]
    assert {0, 1, 2, 3} in groups and {4, 5, 6} in groups
    assert not result.leftover


def test_matching_against_existing_person_centroid():
    known = _synthetic_person(7, 5)
    centroids = {42: centroid(np.stack(known))}

    new_same = _synthetic_person(7, 2)  # same base vector as person 42
    stranger = _synthetic_person(99, 1)
    embs = np.stack(new_same + stranger)

    result = cluster_faces([10, 11, 12], embs, centroids,
                           match_threshold=0.5, min_cluster_size=2)

    assert result.matched == {10: 42, 11: 42}
    assert result.leftover == [12]  # single stranger below min_cluster_size
    assert not result.new_clusters


def test_singletons_stay_unknown():
    embs = np.stack([_synthetic_person(s, 1)[0] for s in (11, 22, 33)])
    result = cluster_faces([1, 2, 3], embs, {}, match_threshold=0.5, min_cluster_size=2)
    assert not result.new_clusters
    assert sorted(result.leftover) == [1, 2, 3]


def test_centroid_is_normalized():
    c = centroid(np.stack(_synthetic_person(5, 10)))
    assert abs(np.linalg.norm(c) - 1.0) < 1e-6
