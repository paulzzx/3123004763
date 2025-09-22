#!/usr/bin/env python3
import argparse, sys, runpy, os
from pathlib import Path
import cProfile, pstats

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", required=True)
    ap.add_argument("--orig", required=True)
    ap.add_argument("--plag", required=True)
    ap.add_argument("--ans", required=True)
    ap.add_argument("--out", default="profiles/run.prof")
    args = ap.parse_args()

    prof_out = Path(args.out)
    prof_out.parent.mkdir(parents=True, exist_ok=True)
    Path(args.ans).parent.mkdir(parents=True, exist_ok=True)

    import sys, os
    proj_root = os.path.abspath(os.path.join(os.path.dirname(args.main), "."))
    sys.path.insert(0, proj_root)

    argv_backup = sys.argv[:]
    sys.argv = [str(Path(args.main).resolve()), args.orig, args.plag, args.ans]

    profiler = cProfile.Profile()
    try:
        profiler.enable()
        try:
            runpy.run_path(sys.argv[0], run_name="__main__")
        except SystemExit:
            # main.py 很可能会调用 sys.exit()，这里吞掉，不让整个脚本提前退出
            pass
        finally:
            profiler.disable()
    finally:
        sys.argv = argv_backup
        profiler.dump_stats(str(prof_out))
        print(f"[OK] Wrote cProfile stats to: {prof_out}")

if __name__ == "__main__":
    main()
