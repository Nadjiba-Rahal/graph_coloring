#pragma once
#ifndef COLORING_H
#define COLORING_H

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <limits.h>

#ifdef _WIN32
  #include <windows.h>
  #define EXPORT __declspec(dllexport)
  static inline double now_s(void) {
      LARGE_INTEGER freq, cnt;
      QueryPerformanceFrequency(&freq);
      QueryPerformanceCounter(&cnt);
      return (double)cnt.QuadPart / (double)freq.QuadPart;
  }
#else
  #include <sys/time.h>
  #define EXPORT
  static inline double now_s(void) {
      struct timeval tv;
      gettimeofday(&tv, NULL);
      return tv.tv_sec + tv.tv_usec * 1e-6;
  }
#endif

/* ── ColorSet: bitset for up to 63 colors ─────────────────────────────
   All standard DIMACS benchmarks (DSJC125.x, queen*, etc.) stay under 63.
   ─────────────────────────────────────────────────────────────────── */
typedef uint64_t ColorSet;

#define CS_ADD(s,c)   ((s) |=  (1ULL << (c)))
#define CS_HAS(s,c)   (((s)  >> (c)) & 1ULL)
#define CS_DEL(s,c)   ((s) &= ~(1ULL << (c)))
#define CS_COUNT(s)   __builtin_popcountll(s)
#define CS_LOWEST(s)  __builtin_ctzll(s)

static inline ColorSet cs_mask(int ub) {
    if (ub <= 0)  return 0ULL;
    if (ub >= 64) return ~0ULL;
    return (1ULL << ub) - 1ULL;
}

/* ── Progress callback (fired every 500 B&B nodes) ── */
typedef void (*ProgressCB)(long nodes, int UB, int LB, double t, long cuts);

/* ── B&B state shared by both algorithms ─────────────────────────────
   Graph pointers are NOT owned by this struct (owned by caller).
   All other arrays ARE allocated/freed by the solver function.
   ─────────────────────────────────────────────────────────────────── */
typedef struct {
    /* graph (borrowed) */
    int   n;
    int*  adj;    /* flat CSR adjacency, sorted per vertex             */
    int*  start;  /* start[v] = first index of v's neighbors in adj   */
    int*  deg;    /* degree[v]                                         */

    /* search state (owned) */
    int*      color;       /* current partial coloring; -1 = uncolored */
    ColorSet* cset;        /* for each vertex: bitset of adjacent colors */
    int*      dsat;        /* DSAT saturation degree                    */

    /* bounds */
    int   UB;              /* current best upper bound (# colors used)  */
    int   LB;              /* global lower bound                        */
    int*  best_color;      /* best coloring found (points to caller buf)*/

    /* stats */
    long  nodes_visited;
    long  branches_cut;

    /* time */
    double time_start;
    int    temps_max;
    int    timeout;

    /* callback */
    ProgressCB callback;
} BBState;

/* ── Binary search in sorted adjacency list ─────────────────────────── */
static inline int adj_has(const int* adj, int sv, int dv, int target) {
    int lo = sv, hi = sv + dv - 1;
    while (lo <= hi) {
        int mid = (lo + hi) >> 1;
        if      (adj[mid] == target) return 1;
        else if (adj[mid] <  target) lo = mid + 1;
        else                          hi = mid - 1;
    }
    return 0;
}

/* ── Assign color c to vertex v, update DSAT of uncolored neighbors ── */
static inline void colorier(BBState* s, int v, int c) {
    s->color[v] = c;
    for (int j = s->start[v]; j < s->start[v] + s->deg[v]; j++) {
        int w = s->adj[j];
        if (s->color[w] != -1) continue;
        if (!CS_HAS(s->cset[w], c)) { CS_ADD(s->cset[w], c); s->dsat[w]++; }
    }
}

/* ── Remove color c from vertex v, restore DSAT of uncolored neighbors */
static inline void decolorier(BBState* s, int v, int c) {
    s->color[v] = -1;
    for (int j = s->start[v]; j < s->start[v] + s->deg[v]; j++) {
        int w = s->adj[j];
        if (s->color[w] != -1) continue;
        if (!CS_HAS(s->cset[w], c)) continue;
        /* Color c still present via another colored neighbor of w? */
        int still = 0;
        for (int k = s->start[w]; k < s->start[w] + s->deg[w] && !still; k++) {
            int x = s->adj[k];
            if (x != v && s->color[x] == c) still = 1;
        }
        if (!still) { CS_DEL(s->cset[w], c); s->dsat[w]--; }
    }
}

/* ── Standard DSATUR vertex selection (no extra tie-breaking) ─────── */
static inline int select_dsatur(const BBState* s) {
    int best = -1;
    for (int v = 0; v < s->n; v++) {
        if (s->color[v] != -1) continue;
        if (best == -1) { best = v; continue; }
        if (s->dsat[v] > s->dsat[best] ||
           (s->dsat[v] == s->dsat[best] && s->deg[v] > s->deg[best]))
            best = v;
    }
    return best;
}

/* ── Fire progress callback every 500 nodes ─────────────────────────── */
static inline void maybe_cb(BBState* s) {
    if (!s->callback) return;
    if (s->nodes_visited == 1 || s->nodes_visited % 500 == 0) {
        double t = now_s() - s->time_start;
        s->callback(s->nodes_visited, s->UB, s->LB, t, s->branches_cut);
    }
}

#endif /* COLORING_H */
