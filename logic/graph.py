"""
logic/graph.py
──────────────
DIMACS .col parser and graph utility functions.
Returns data in CSR (Compressed Sparse Row) format for direct C interop.
"""

from collections import defaultdict


# ── DIMACS parser ─────────────────────────────────────────────────────────

def parse_dimacs(content: bytes) -> dict:
    """
    Parse a DIMACS .col file.

    Returns
    -------
    dict with keys:
        n        : int           – number of vertices
        m        : int           – number of edges
        voisins  : list[list]    – adjacency list (sorted, 0-indexed)
        adj_flat : list[int]     – CSR flat adjacency
        start    : list[int]     – CSR start indices
        deg      : list[int]     – degree of each vertex
    """
    n = 0
    adj: dict[int, set] = defaultdict(set)

    for raw in content.decode(errors="replace").splitlines():
        line = raw.strip()
        if not line or line[0] == 'c':
            continue
        parts = line.split()
        if line[0] == 'p' and len(parts) >= 3:
            n = int(parts[2])
        elif line[0] == 'e' and len(parts) >= 3:
            u, v = int(parts[1]) - 1, int(parts[2]) - 1
            adj[u].add(v)
            adj[v].add(u)

    if n == 0:
        raise ValueError("No vertices found – check the DIMACS file format.")

    voisins   = [sorted(adj[i]) for i in range(n)]
    deg       = [len(voisins[i]) for i in range(n)]
    m         = sum(deg) // 2

    # Build CSR
    start = [0] * n
    for i in range(1, n):
        start[i] = start[i - 1] + deg[i - 1]
    adj_flat = [v for nb in voisins for v in nb]

    density = m / (n * (n - 1) / 2) * 100 if n > 1 else 0.0

    return {
        "n":        n,
        "m":        m,
        "density":  round(density, 2),
        "voisins":  voisins,
        "adj_flat": adj_flat,
        "start":    start,
        "deg":      deg,
    }
