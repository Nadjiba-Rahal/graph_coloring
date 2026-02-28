/*
 * heuristics.c
 * ─────────────
 * greedy_clique : greedy maximum clique (lower bound for χ)
 * dsatur        : DSATUR colouring heuristic (upper bound for χ)
 */

#include <stdlib.h>
#include <string.h>
#include "coloring.h"

/* ── Insertion-sort an int array by key[arr[i]] descending ─────────── */
static void isort_desc(int* arr, int len, const int* key) {
    for (int i = 1; i < len; i++) {
        int val = arr[i], j = i - 1;
        while (j >= 0 && key[arr[j]] < key[val]) { arr[j+1] = arr[j]; j--; }
        arr[j+1] = val;
    }
}

/* ── Greedy max clique ──────────────────────────────────────────────────
 * Order vertices by degree descending, greedily extend clique.
 * Returns ω(G) approximation (valid lower bound for χ(G)).
 * ─────────────────────────────────────────────────────────────────── */
EXPORT int greedy_clique(int n, const int* adj, const int* start, const int* deg) {
    if (n <= 0) return 0;

    int* order = (int*)malloc(n * sizeof(int));
    int* clique = (int*)malloc(n * sizeof(int));
    if (!order || !clique) { free(order); free(clique); return 1; }

    for (int i = 0; i < n; i++) order[i] = i;
    isort_desc(order, n, deg);

    int clique_sz = 0;
    for (int i = 0; i < n; i++) {
        int v = order[i], ok = 1;
        for (int j = 0; j < clique_sz && ok; j++)
            ok = adj_has(adj, start[v], deg[v], clique[j]);
        if (ok) clique[clique_sz++] = v;
    }

    int result = clique_sz;
    free(order); free(clique);
    return result;
}

/* ── DSATUR heuristic colouring ────────────────────────────────────────
 * Returns χ_DSATUR (valid upper bound for χ(G)).
 * Writes the colouring into out_coloring[0..n-1].
 * ─────────────────────────────────────────────────────────────────── */
EXPORT int dsatur(int n, const int* adj, const int* start, const int* deg,
                  int* out_coloring) {
    if (n <= 0) return 0;

    for (int i = 0; i < n; i++) out_coloring[i] = -1;

    ColorSet* cset = (ColorSet*)calloc(n, sizeof(ColorSet));
    int*      dsat = (int*)calloc(n, sizeof(int));
    if (!cset || !dsat) { free(cset); free(dsat); return 0; }

    for (int iter = 0; iter < n; iter++) {
        /* Select vertex: max DSAT, tie-break max degree */
        int u = -1;
        for (int v = 0; v < n; v++) {
            if (out_coloring[v] != -1) continue;
            if (u == -1 ||
                dsat[v] > dsat[u] ||
               (dsat[v] == dsat[u] && deg[v] > deg[u]))
                u = v;
        }

        /* Assign smallest available color */
        int c = 0;
        while (CS_HAS(cset[u], c)) c++;
        out_coloring[u] = c;

        /* Update uncolored neighbors */
        for (int j = start[u]; j < start[u] + deg[u]; j++) {
            int w = adj[j];
            if (out_coloring[w] != -1) continue;
            if (!CS_HAS(cset[w], c)) { CS_ADD(cset[w], c); dsat[w]++; }
        }
    }

    int max_c = 0;
    for (int v = 0; v < n; v++)
        if (out_coloring[v] > max_c) max_c = out_coloring[v];

    free(cset); free(dsat);
    return max_c + 1;
}
