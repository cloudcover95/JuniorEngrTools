"""Lean TDA compute for EngrTools. Numpy only. No giotto."""
from __future__ import annotations
import numpy as np

def pairwise_sq(points):
    x = np.asarray(points, dtype=np.float64)
    x2 = np.square(x).sum(axis=1)
    d = x2[:, None] + x2[None, :] - 2.0 * x @ x.T
    np.maximum(d, 0.0, out=d)
    return d

def h0(points):
    x = np.asarray(points, dtype=np.float64)
    n = x.shape[0]
    d2 = pairwise_sq(x)
    edges = sorted((float(d2[i, j]) ** 0.5, i, j) for i in range(n) for j in range(i + 1, n))
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    deaths = []
    comp = n
    for dist, i, j in edges:
        a, b = find(i), find(j)
        if a != b:
            parent[a] = b
            comp -= 1
            deaths.append(dist)
            if comp == 1:
                break
    return {"beta0": comp, "n_merges": len(deaths), "mean_death": float(np.mean(deaths)) if deaths else 0.0}

def summary(points, eps=None):
    x = np.asarray(points, dtype=np.float64)
    d2 = pairwise_sq(x)
    i, j = np.triu_indices(x.shape[0], 1)
    dist = np.sqrt(d2[i, j])
    if eps is None:
        eps = float(np.median(dist)) if dist.size else 0.0
    e = int((dist <= eps).sum())
    h = h0(x)
    return {"n": int(x.shape[0]), "eps": eps, "edges": e, "beta0": h["beta0"],
            "h1_graph": int(e - x.shape[0] + h["beta0"]), "mean_death": h["mean_death"]}

if __name__ == "__main__":
    import json
    rng = np.random.default_rng(7)
    print(json.dumps(summary(rng.normal(size=(20, 3))), indent=2))
