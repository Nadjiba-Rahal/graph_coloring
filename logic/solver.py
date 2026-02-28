"""
logic/solver.py
───────────────
Auto-compiles the C shared library on first import, then exposes:

    solve_sewell(graph_data, temps_max, live_state=None) -> dict
    solve_furini(graph_data, temps_max, live_state=None) -> dict

graph_data is the dict returned by logic.graph.parse_dimacs().
live_state is an optional shared dict updated every 500 B&B nodes
(used by the live race panel in the UI).

The C library is compiled once into:
    logic/coloring.dll   (Windows)
    logic/coloring.so    (Linux / macOS)

Requirements: gcc must be on PATH.
"""

import ctypes
import os
import platform
import subprocess
import sys

# ── Locate the logic directory ────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))

_C_SOURCES = [
    os.path.join(_HERE, "heuristics.c"),
    os.path.join(_HERE, "bb_sewell.c"),
    os.path.join(_HERE, "bb_furini.c"),
]

_IS_WINDOWS = platform.system() == "Windows"
_LIB_NAME   = "coloring.dll" if _IS_WINDOWS else "coloring.so"
_LIB_PATH   = os.path.join(_HERE, _LIB_NAME)


# ── Compile C sources → shared library ───────────────────────────────────

def _compile():
    """Compile C sources into a shared library. Raises RuntimeError on failure."""
    flags = [
        "gcc", "-O2", "-std=c99",
        "-shared",
        *(["-static-libgcc"] if _IS_WINDOWS else ["-fPIC"]),
        "-I", _HERE,
        "-o", _LIB_PATH,
        *_C_SOURCES,
    ]
    try:
        result = subprocess.run(
            flags,
            capture_output=True, text=True, timeout=60,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "gcc not found on PATH.\n"
            "Windows: install MinGW-w64 and add its bin/ directory to PATH.\n"
            "Linux  : sudo apt install gcc\n"
            "macOS  : xcode-select --install"
        )
    if result.returncode != 0:
        raise RuntimeError(f"C compilation failed:\n{result.stderr}")


def _needs_recompile() -> bool:
    if not os.path.exists(_LIB_PATH):
        return True
    lib_mtime = os.path.getmtime(_LIB_PATH)
    for src in _C_SOURCES + [os.path.join(_HERE, "coloring.h"),
                               os.path.join(_HERE, "heuristics.h")]:
        if os.path.exists(src) and os.path.getmtime(src) > lib_mtime:
            return True
    return False


# ── Load library ─────────────────────────────────────────────────────────

def _load_lib() -> ctypes.CDLL:
    if _needs_recompile():
        _compile()
    try:
        lib = ctypes.CDLL(_LIB_PATH)
    except OSError as e:
        raise RuntimeError(f"Cannot load compiled library: {e}")

    # ── Progress callback type ─────────────────────────────────────────
    # void (*ProgressCB)(long nodes, int UB, int LB, double t, long cuts)
    global _CB_TYPE
    _CB_TYPE = ctypes.CFUNCTYPE(
        None,
        ctypes.c_long,   # nodes
        ctypes.c_int,    # UB
        ctypes.c_int,    # LB
        ctypes.c_double, # t
        ctypes.c_long,   # cuts
    )

    # ── sewell_solve signature ─────────────────────────────────────────
    lib.sewell_solve.restype  = None
    lib.sewell_solve.argtypes = [
        ctypes.c_int,                        # n
        ctypes.POINTER(ctypes.c_int),        # adj
        ctypes.POINTER(ctypes.c_int),        # start
        ctypes.POINTER(ctypes.c_int),        # deg
        ctypes.c_int,                        # temps_max
        _CB_TYPE,                            # callback
        ctypes.POINTER(ctypes.c_int),        # out_K
        ctypes.POINTER(ctypes.c_int),        # out_coloring[n]
        ctypes.POINTER(ctypes.c_int),        # out_LB
        ctypes.POINTER(ctypes.c_int),        # out_UB_init
        ctypes.POINTER(ctypes.c_int),        # out_optimal
        ctypes.POINTER(ctypes.c_long),       # out_nodes
        ctypes.POINTER(ctypes.c_long),       # out_cuts
        ctypes.POINTER(ctypes.c_double),     # out_time
        ctypes.POINTER(ctypes.c_int),        # out_timeout
    ]

    # ── furini_solve signature (identical layout) ──────────────────────
    lib.furini_solve.restype  = None
    lib.furini_solve.argtypes = lib.sewell_solve.argtypes

    return lib


_lib: ctypes.CDLL | None = None
_CB_TYPE = None


def get_lib() -> ctypes.CDLL:
    global _lib
    if _lib is None:
        _lib = _load_lib()
    return _lib


# ── CSR conversion ────────────────────────────────────────────────────────

def _to_csr(graph_data: dict):
    n        = graph_data["n"]
    adj_flat = graph_data["adj_flat"]
    start    = graph_data["start"]
    deg      = graph_data["deg"]
    m        = len(adj_flat)

    c_adj   = (ctypes.c_int * m)(*adj_flat)
    c_start = (ctypes.c_int * n)(*start)
    c_deg   = (ctypes.c_int * n)(*deg)
    return c_adj, c_start, c_deg


# ── Callback factory ──────────────────────────────────────────────────────

def _make_cb(historique: list, live: dict | None):
    def _inner(nodes, UB, LB, t, cuts):
        snap = {"noeuds": nodes, "UB": UB, "LB": LB,
                "temps": t, "coupes": cuts, "done": False}
        historique.append(snap)
        if live is not None:
            live.update(snap)
    return _CB_TYPE(_inner)


# ── Generic solver wrapper ────────────────────────────────────────────────

def _solve(c_func_name: str, algo_name: str,
           graph_data: dict, temps_max: int,
           live_state: dict | None) -> dict:

    lib = get_lib()
    n   = graph_data["n"]

    c_adj, c_start, c_deg = _to_csr(graph_data)
    historique: list = []
    cb = _make_cb(historique, live_state)

    c_coloring = (ctypes.c_int * n)()
    out_K      = ctypes.c_int()
    out_LB     = ctypes.c_int()
    out_UBi    = ctypes.c_int()
    out_opt    = ctypes.c_int()
    out_nodes  = ctypes.c_long()
    out_cuts   = ctypes.c_long()
    out_time   = ctypes.c_double()
    out_tout   = ctypes.c_int()

    func = getattr(lib, c_func_name)
    func(
        ctypes.c_int(n), c_adj, c_start, c_deg,
        ctypes.c_int(temps_max), cb,
        ctypes.byref(out_K), c_coloring,
        ctypes.byref(out_LB), ctypes.byref(out_UBi),
        ctypes.byref(out_opt), ctypes.byref(out_nodes),
        ctypes.byref(out_cuts), ctypes.byref(out_time),
        ctypes.byref(out_tout),
    )

    if live_state is not None:
        live_state.update({"done": True})

    return {
        "algo":            algo_name,
        "K":               out_K.value,
        "coloriage":       list(c_coloring),
        "LB":              out_LB.value,
        "UB_init":         out_UBi.value,
        "optimal":         bool(out_opt.value),
        "noeuds":          out_nodes.value,
        "coupes":          out_cuts.value,
        "temps":           out_time.value,
        "timeout":         bool(out_tout.value),
        "historique_kpi":  historique,
    }


# ── Public API ────────────────────────────────────────────────────────────

def solve_sewell(graph_data: dict, temps_max: int,
                 live_state: dict | None = None) -> dict:
    """Run Sewell (1996) B&B. Returns result dict."""
    return _solve("sewell_solve", "Sewell (1996)",
                  graph_data, temps_max, live_state)


def solve_furini(graph_data: dict, temps_max: int,
                 live_state: dict | None = None) -> dict:
    """Run Furini (2017) B&B. Returns result dict."""
    return _solve("furini_solve", "Furini (2017)",
                  graph_data, temps_max, live_state)


# ── Pre-warm: compile on import ───────────────────────────────────────────
try:
    get_lib()
    _COMPILE_ERROR: str | None = None
except RuntimeError as _e:
    _COMPILE_ERROR = str(_e)
