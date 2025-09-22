
#!/usr/bin/env python3
"""
plot_pstats.py
Load a .prof file (cProfile stats), summarize top hotspots, and produce:
- CSV table of top-N functions by cumulative time
- A bar chart PNG of the same

Usage:
  python scripts/plot_pstats.py profiles/run.prof --top 20 --out profiles/top20.png --csv profiles/top20.csv --project-root .

Notes:
- No third-party deps; uses stdlib + matplotlib.
- Filters out most stdlib/site-packages frames by default; tune with --keep-stdlib if needed.
"""
import argparse, pstats, re, os
from pathlib import Path

def is_stdlib_path(filename: str) -> bool:
    # Heuristic filtering for stdlib/site-packages noise.
    if not filename:
        return True
    lowered = filename.replace('\\','/').lower()
    return any(seg in lowered for seg in [
        "/lib/python", "site-packages", "importlib", "encodings", "zipimport", "threading.py",
        "_bootstrap", "selectors.py", "selectors.py", "inspect.py", "abc.py"
    ])

def format_key(func_tuple):
    filename, lineno, funcname = func_tuple
    return f"{filename}:{lineno}::{funcname}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prof", help=".prof file from cProfile")
    ap.add_argument("--top", type=int, default=20, help="Top N by cumulative time")
    ap.add_argument("--out", default="profiles/top.png", help="Output PNG for bar chart")
    ap.add_argument("--csv", default="profiles/top.csv", help="Output CSV path")
    ap.add_argument("--project-root", default=".", help="Project root to help filter frames")
    ap.add_argument("--keep-stdlib", dest="keep_stdlib", action="store_true", help="Do not filter stdlib/site-packages")
    args = ap.parse_args()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.csv).parent.mkdir(parents=True, exist_ok=True)

    stats = pstats.Stats(args.prof)
    # Normalize and sort by cumulative time
    stats.strip_dirs().sort_stats("cumtime")

    rows = []
    for func, stat in stats.stats.items():
        cc, nc, tt, ct, callers = stat  # primitive calls, total calls, tottime, cumtime, callers
        filename, lineno, funcname = func
        if not args.keep_stdlib and is_stdlib_path(filename):
            # Keep if file appears inside project root
            pr = os.path.abspath(args.project_root)
            try:
                abspath = os.path.abspath(filename)
            except Exception:
                abspath = filename
            if not (pr and isinstance(abspath, str) and abspath.startswith(pr)):
                continue
        rows.append({
            "func": format_key(func),
            "calls": nc,
            "primitive_calls": cc,
            "tottime": tt,
            "cumtime": ct,
        })

    # Sort by cumtime desc and take top N
    rows.sort(key=lambda r: r["cumtime"], reverse=True)
    top_rows = rows[:args.top]

    # Write CSV
    import csv
    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["rank","func","calls","primitive_calls","tottime","cumtime"])
        w.writeheader()
        for i, r in enumerate(top_rows, 1):
            row = {"rank": i}
            row.update(r)
            w.writerow(row)
    print(f"[OK] Wrote CSV: {args.csv}")

    # Bar chart
    import matplotlib.pyplot as plt
    labels = [r["func"] for r in top_rows][::-1]  # reverse for horizontal plot
    values = [r["cumtime"] for r in top_rows][::-1]

    plt.figure(figsize=(10, max(4, len(labels) * 0.45)))
    plt.barh(range(len(labels)), values)
    plt.yticks(range(len(labels)), labels, fontsize=8)
    plt.xlabel("Cumulative time (s)")
    plt.title("Top functions by cumulative time")
    plt.tight_layout()
    plt.savefig(args.out, dpi=200)
    plt.close()
    print(f"[OK] Wrote plot: {args.out}")

if __name__ == "__main__":
    main()
