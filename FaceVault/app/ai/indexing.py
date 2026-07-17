"""In-memory vector index for face similarity search.

The index is a disposable cache rebuilt from the database — never the
source of truth. Brute-force cosine over normalized float32 embeddings:
one matrix-vector product, comfortably fast to ~1M vectors. If FAISS is
installed it is used automatically for larger libraries.
"""

import numpy as np

try:  # optional accelerator, never required
    import faiss  # type: ignore

    _HAS_FAISS = True
except ImportError:
    _HAS_FAISS = False

_FAISS_MIN_VECTORS = 50_000  # below this, brute force is faster than the overhead


class VectorIndex:
    def __init__(self, dim: int = 128):
        self.dim = dim
        self._ids: list[int] = []
        self._matrix: np.ndarray | None = None
        self._faiss = None

    def build(self, ids: list[int], matrix: np.ndarray | None) -> None:
        self._ids = list(ids)
        self._faiss = None
        if matrix is None or len(ids) == 0:
            self._matrix = None
            return
        self._matrix = np.ascontiguousarray(matrix, dtype=np.float32)
        if _HAS_FAISS and len(ids) >= _FAISS_MIN_VECTORS:
            index = faiss.IndexFlatIP(self.dim)
            index.add(self._matrix)
            self._faiss = index

    def __len__(self) -> int:
        return len(self._ids)

    def search(self, query: np.ndarray, k: int = 10) -> list[tuple[int, float]]:
        """Return [(face_id, cosine_similarity)] best-first."""
        if self._matrix is None:
            return []
        q = np.asarray(query, dtype=np.float32).reshape(1, -1)
        k = min(k, len(self._ids))
        if self._faiss is not None:
            sims, idxs = self._faiss.search(q, k)
            return [
                (self._ids[i], float(s))
                for i, s in zip(idxs[0], sims[0])
                if i != -1
            ]
        sims = (self._matrix @ q.T).flatten()
        top = np.argsort(-sims)[:k]
        return [(self._ids[i], float(sims[i])) for i in top]
