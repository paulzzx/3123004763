from __future__ import annotations
import os
import sys
from typing import List, Optional, Dict
from src.io_utils import read_text, write_text
from src.pipeline import Config, compute_similarity

def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1","true","yes","on"}

def _load_syn_file(path: Optional[str]) -> Optional[Dict[str,str]]:
    if not path:
        return None
    mapping: Dict[str,str] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("\t")
                if len(parts) == 2:
                    mapping[parts[0]] = parts[1]
    except FileNotFoundError:
        return None
    return mapping

def safe_main(argv: List[str]) -> int:
    if len(argv) != 4:
        sys.stderr.write("Usage: python main.py <orig_abs_path> <plag_abs_path> <ans_abs_path>\n")
        return 2
    _, orig_path, plag_path, ans_path = argv
    try:
        orig = read_text(orig_path)
        plag = read_text(plag_path)
        n = int(os.getenv("NGRAM", "3"))
        method = os.getenv("METHOD", "jaccard").strip().lower()
        use_syn = _env_bool("USE_SYNONYMS", False)
        use_edit = _env_bool("USE_EDIT_FALLBACK", False)
        syn_file = os.getenv("SYN_FILE")
        synonyms = _load_syn_file(syn_file) if use_syn else None

        cfg = Config(n=n, method=method, use_synonyms=use_syn, use_edit_fallback=use_edit, synonyms=synonyms)
        score = compute_similarity(orig, plag, cfg)
        percent = f"{score * 100:.2f}"
        write_text(ans_path, percent)
        return 0
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        try:
            write_text(ans_path, "0.00")
        except Exception:
            pass
        return 1

if __name__ == "__main__":
    sys.exit(safe_main(sys.argv))
