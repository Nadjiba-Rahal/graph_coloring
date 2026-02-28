#pragma once
#ifndef HEURISTICS_H
#define HEURISTICS_H

/* ── Greedy max clique ──────────────────────────────────────────────────
 * Order vertices by degree descending, greedily extend clique.
 * Returns ω(G) approximation (valid lower bound for χ(G)).
 * ─────────────────────────────────────────────────────────────────── */
EXPORT int greedy_clique(int n, const int* adj, const int* start, const int* deg);

/* ── DSATUR heuristic colouring ────────────────────────────────────────
 * Returns χ_DSATUR (valid upper bound for χ(G)).
 * Writes the colouring into out_coloring[0..n-1].
 * ─────────────────────────────────────────────────────────────────── */
EXPORT int dsatur(int n, const int* adj, const int* start, const int* deg,
                  int* out_coloring);

#endif
