/*
 * bb_sewell.c
 * ───────────
 * Sewell (1996) DSATUR B&B with tie-breaking rule:
 *   Among vertices with the same max-DSAT and max-degree, choose the one
 *   that *maximises* the number of shared available-colour options with
 *   its uncoloured neighbours (bitset intersection).
 *
 * Reference:
 *   E.R. Sewell, "An improved algorithm for exact graph coloring",
 *   DIMACS Series Discrete Math. Theoret. Comput. Sci., 1996.
 */

#include "coloring.h"
#include "heuristics.h"
#include <string.h>
#include <stdlib.h>

/* ── Sewell vertex selection ───────────────────────────────────────────
 * 1. Max DSAT
 * 2. Tie-break: max degree
 * 3. Tie-break: max Σ_{uncoloured u ∈ N(v)} |opts(v) ∩ opts(u)|
 *    where opts(v) = {0..UB-1} \ cset[v]
 * ─────────────────────────────────────────────────────────────────── */
static int select_sewell(const BBState* s) {
    if (s->n <= 0) return -1;

    /* Pass 1: find max_dsat, max_deg */
    int max_dsat = -1, max_deg = -1;
    for (int v = 0; v < s->n; v++) {
        if (s->color[v] != -1) continue;
        if (s->dsat[v] > max_dsat) max_dsat = s->dsat[v];
    }
    for (int v = 0; v < s->n; v++) {
        if (s->color[v] != -1 || s->dsat[v] != max_dsat) continue;
        if (s->deg[v] > max_deg) max_deg = s->deg[v];
    }

    /* Pass 2: collect candidates */
    int cands[1024];  /* n ≤ 10000 but typical benchmarks ≤ 500 */
    int nc = 0, first = -1;
    for (int v = 0; v < s->n; v++) {
        if (s->color[v] != -1 || s->dsat[v] != max_dsat || s->deg[v] != max_deg)
            continue;
        if (first == -1) first = v;
        if (nc < 1024) cands[nc] = v;
        nc++;
    }
    if (nc <= 1 || s->UB >= 63) return first;

    /* Pass 3: Sewell tie-breaking */
    ColorSet mask = cs_mask(s->UB);
    int best = first, best_score = -1;

    for (int i = 0; i < nc; i++) {
        int v = cands[i];
        ColorSet opts_v = mask & ~s->cset[v];
        int score = 0;
        for (int j = s->start[v]; j < s->start[v] + s->deg[v]; j++) {
            int u = s->adj[j];
            if (s->color[u] != -1) continue;
            score += CS_COUNT(opts_v & (mask & ~s->cset[u]));
        }
        if (score > best_score) { best_score = score; best = v; }
    }
    return best;
}

/* ── Recursive B&B ─────────────────────────────────────────────────── */
static void explore(BBState* s, int nb_col, int k) {
    /* Time check */
    if (now_s() - s->time_start > (double)s->temps_max) { s->timeout = 1; return; }

    s->nodes_visited++;
    maybe_cb(s);

    /* Leaf: complete coloring */
    if (nb_col == s->n) {
        if (k < s->UB) {
            s->UB = k;
            memcpy(s->best_color, s->color, s->n * sizeof(int));
        }
        return;
    }

    /* Pruning: current cost already ≥ best */
    if (k >= s->UB - 1) { s->branches_cut++; return; }

    int v = select_sewell(s);
    if (v == -1) return;

    int c_limit = (k + 1 < s->UB) ? k + 1 : s->UB - 1;
    for (int c = 0; c < c_limit; c++) {
        if (CS_HAS(s->cset[v], c)) continue;
        int new_k = (c + 1 > k) ? c + 1 : k;
        if (new_k >= s->UB) continue;

        colorier(s, v, c);
        explore(s, nb_col + 1, new_k);
        decolorier(s, v, c);

        if (s->timeout || s->UB == s->LB) return;
    }
}

/* ── Public solver function ────────────────────────────────────────────
 * All out_* arguments are pre-allocated by the caller.
 * out_coloring must be int[n].
 * ─────────────────────────────────────────────────────────────────── */
EXPORT void sewell_solve(
    int n, int* adj, int* start, int* deg,
    int temps_max, ProgressCB cb,
    int* out_K, int* out_coloring,
    int* out_LB, int* out_UB_init,
    int* out_optimal, long* out_nodes, long* out_cuts,
    double* out_time, int* out_timeout
) {
    BBState s;
    s.n = n; s.adj = adj; s.start = start; s.deg = deg;

    s.color      = (int*)malloc(n * sizeof(int));
    s.cset       = (ColorSet*)calloc(n, sizeof(ColorSet));
    s.dsat       = (int*)calloc(n, sizeof(int));
    s.best_color = out_coloring;

    for (int i = 0; i < n; i++) s.color[i] = -1;

    s.nodes_visited = 0; s.branches_cut = 0;
    s.temps_max = temps_max; s.timeout = 0;
    s.callback  = cb;
    s.time_start = now_s();

    /* Initial bounds */
    s.LB = greedy_clique(n, adj, start, deg);

    int* init_col = (int*)malloc(n * sizeof(int));
    int ub_init   = dsatur(n, adj, start, deg, init_col);
    s.UB = ub_init;
    memcpy(s.best_color, init_col, n * sizeof(int));
    free(init_col);

    *out_LB     = s.LB;
    *out_UB_init = ub_init;

    /* B&B */
    if (n > 0 && s.LB < s.UB)
        explore(&s, 0, 0);

    *out_K       = s.UB;
    *out_optimal = (s.UB == s.LB) && !s.timeout;
    *out_nodes   = s.nodes_visited;
    *out_cuts    = s.branches_cut;
    *out_time    = now_s() - s.time_start;
    *out_timeout = s.timeout;

    free(s.color); free(s.cset); free(s.dsat);
}
