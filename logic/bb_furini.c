/*
 * bb_furini.c
 * ───────────
 * Furini, Gabrel & Ternier (2017) — Networks 69(2):124-141
 *
 * Key contribution: recompute a tighter lower bound at EVERY B&B node
 * using a "Reduced Graph" R built from the current partial coloring.
 *
 * REDUCED GRAPH R
 * ───────────────
 *  Nodes
 *    s_c  : one super-node per used color class  c ∈ {0..k-1}
 *    u    : one node per uncolored vertex
 *
 *  Edges
 *    s_c ── s_d   iff  ∃ uncolored u : u sees both color c AND color d
 *                      ⟺ sees[c] ∩ sees[d] ≠ ∅
 *    s_c ── u     iff  u is adjacent to ≥1 vertex of color c
 *                      ⟺ c ∈ cset[u]
 *     u  ── w     iff  u and w are adjacent in G
 *
 *  Any clique Q in R needs |Q| distinct colors  ⟹  χ*(G) ≥ |Q|.
 *  We approximate ω(R) with a greedy clique sorted by degree in R.
 *
 * This bound is what enabled Furini et al. to prove χ*(DSJC125.9) = 44.
 */

#include "coloring.h"
#include "heuristics.h"
#include <stdlib.h>
#include <string.h>

/* ── Reduced-graph lower bound ─────────────────────────────────────────
 * k_used = number of color classes already used at this node.
 * Returns ω(R), a valid lower bound for χ*(G).
 * ─────────────────────────────────────────────────────────────────── */
static int lb_reduced(BBState* s, int k_used) {

    /* ── Collect uncolored vertices ── */
    int* uncolored = (int*)malloc(s->n * sizeof(int));
    int nu = 0;
    for (int v = 0; v < s->n; v++)
        if (s->color[v] == -1) uncolored[nu++] = v;

    if (nu == 0) { free(uncolored); return k_used; }

    /* ── Trivial case: no color class yet → greedy clique on whole graph ── */
    if (k_used == 0) {
        int* subdeg = (int*)calloc(s->n, sizeof(int));
        for (int i = 0; i < nu; i++) {
            int v = uncolored[i];
            for (int j = s->start[v]; j < s->start[v] + s->deg[v]; j++)
                if (s->color[s->adj[j]] == -1) subdeg[v]++;
        }
        /* insertion-sort uncolored by subdeg desc */
        for (int i = 1; i < nu; i++) {
            int key = uncolored[i], j2 = i - 1;
            while (j2 >= 0 && subdeg[uncolored[j2]] < subdeg[key]) {
                uncolored[j2+1] = uncolored[j2]; j2--;
            }
            uncolored[j2+1] = key;
        }
        int* clique = (int*)malloc(nu * sizeof(int));
        int csz = 0;
        for (int i = 0; i < nu; i++) {
            int v = uncolored[i], ok = 1;
            for (int j = 0; j < csz && ok; j++)
                ok = adj_has(s->adj, s->start[v], s->deg[v], clique[j]);
            if (ok) clique[csz++] = v;
        }
        int res = csz;
        free(subdeg); free(clique); free(uncolored);
        return res;
    }

    /* ── sees[c][i] = 1 iff uncolored[i] is adjacent to color class c ─── */
    /* Memory layout: sees[c * nu + i]                                       */
    size_t sees_sz = (size_t)k_used * nu;
    uint8_t* sees = (uint8_t*)calloc(sees_sz, 1);
    if (!sees) { free(uncolored); return k_used; } /* safe fallback */

    for (int i = 0; i < nu; i++) {
        int u = uncolored[i];
        ColorSet cs = s->cset[u];
        while (cs) {
            int c = CS_LOWEST(cs); cs &= cs - 1;
            if (c < k_used) sees[(size_t)c * nu + i] = 1;
        }
    }

    /* ── super_adj[c * k_used + d] = 1 iff sees[c] ∩ sees[d] ≠ ∅ ────── */
    uint8_t* sadj = (uint8_t*)calloc((size_t)k_used * k_used, 1);
    if (!sadj) { free(sees); free(uncolored); return k_used; }

    for (int c = 0; c < k_used; c++) {
        uint8_t* sc = sees + (size_t)c * nu;
        for (int d = c + 1; d < k_used; d++) {
            uint8_t* sd = sees + (size_t)d * nu;
            int overlap = 0;
            for (int i = 0; i < nu && !overlap; i++)
                if (sc[i] && sd[i]) overlap = 1;
            if (overlap) sadj[c * k_used + d] = sadj[d * k_used + c] = 1;
        }
    }

    /* ── Degree in R for each node ──────────────────────────────────────
     * Encoding: node id < k_used  → super-node id
     *           node id >= k_used → uncolored[id - k_used]
     * ─────────────────────────────────────────────────────────────────*/
    int total = k_used + nu;
    int* degR = (int*)calloc(total, sizeof(int));

    for (int c = 0; c < k_used; c++) {
        uint8_t* sc = sees + (size_t)c * nu;
        for (int d = 0; d < k_used; d++) if (sadj[c * k_used + d]) degR[c]++;
        for (int i = 0; i < nu; i++)    if (sc[i])                  degR[c]++;
    }
    for (int i = 0; i < nu; i++) {
        int v = uncolored[i];
        degR[k_used + i] = (int)CS_COUNT(s->cset[v]); /* super-node edges */
        for (int j = s->start[v]; j < s->start[v] + s->deg[v]; j++)
            if (s->color[s->adj[j]] == -1) degR[k_used + i]++;
    }

    /* ── Sort all nodes by degR descending (insertion sort) ─────────── */
    int* nodes = (int*)malloc(total * sizeof(int));
    for (int i = 0; i < total; i++) nodes[i] = i;
    for (int i = 1; i < total; i++) {
        int key = nodes[i], j = i - 1;
        while (j >= 0 && degR[nodes[j]] < degR[key]) { nodes[j+1] = nodes[j]; j--; }
        nodes[j+1] = key;
    }

    /* ── Greedy max clique in R ─────────────────────────────────────── */
    int* clique = (int*)malloc(total * sizeof(int));
    int csz = 0;

    for (int i = 0; i < total; i++) {
        int a = nodes[i], ok = 1;

        for (int j = 0; j < csz && ok; j++) {
            int b = clique[j];
            int adj_ab;

            if (a < k_used && b < k_used) {
                /* super ── super */
                adj_ab = sadj[a * k_used + b];

            } else if (a < k_used) {
                /* super a ── uncolored b */
                adj_ab = sees[(size_t)a * nu + (b - k_used)];

            } else if (b < k_used) {
                /* uncolored a ── super b */
                adj_ab = sees[(size_t)b * nu + (a - k_used)];

            } else {
                /* uncolored ── uncolored: check adjacency in G */
                int va = uncolored[a - k_used];
                int vb = uncolored[b - k_used];
                adj_ab = adj_has(s->adj, s->start[va], s->deg[va], vb);
            }

            if (!adj_ab) ok = 0;
        }
        if (ok) clique[csz++] = a;
    }

    int result = csz;

    free(sees); free(sadj); free(degR); free(nodes);
    free(clique); free(uncolored);
    return result;
}

/* ── Recursive B&B ─────────────────────────────────────────────────── */
static void explore(BBState* s, int nb_col, int k) {
    if (now_s() - s->time_start > (double)s->temps_max) { s->timeout = 1; return; }

    s->nodes_visited++;
    maybe_cb(s);

    /* Leaf */
    if (nb_col == s->n) {
        if (k < s->UB) {
            s->UB = k;
            memcpy(s->best_color, s->color, s->n * sizeof(int));
        }
        return;
    }

    /* Standard pruning */
    if (k >= s->UB - 1) { s->branches_cut++; return; }

    /* ── FURINI: reduced-graph lower bound ──────────────────────────── */
    if (lb_reduced(s, k) >= s->UB) { s->branches_cut++; return; }
    /* ─────────────────────────────────────────────────────────────── */

    int v = select_dsatur(s);
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

/* ── Public solver ─────────────────────────────────────────────────── */
EXPORT void furini_solve(
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

    s.LB = greedy_clique(n, adj, start, deg);

    int* init_col = (int*)malloc(n * sizeof(int));
    int ub_init   = dsatur(n, adj, start, deg, init_col);
    s.UB = ub_init;
    memcpy(s.best_color, init_col, n * sizeof(int));
    free(init_col);

    *out_LB      = s.LB;
    *out_UB_init = ub_init;

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
