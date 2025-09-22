from dataclasses import dataclass
from typing import Dict, Optional
from .normalizer import normalize, apply_synonyms
from .tokenizer import char_ngrams
from .shingler import as_set, as_bag
from .similarity import jaccard, cosine_tf, levenshtein_ratio

@dataclass(frozen=True)
class Config:
    n: int = 3
    method: str = "jaccard"
    use_synonyms: bool = False
    synonyms: Optional[Dict[str, str]] = None
    use_edit_fallback: bool = False

def compute_similarity(orig: str, plag: str, cfg: Config) -> float:
    if cfg.use_synonyms and cfg.synonyms:
        orig = apply_synonyms(orig, cfg.synonyms)
        plag = apply_synonyms(plag, cfg.synonyms)

    o = normalize(orig)
    p = normalize(plag)

    on = char_ngrams(o, cfg.n)
    pn = char_ngrams(p, cfg.n)

    if cfg.method == "jaccard":
        score = jaccard(as_set(on), as_set(pn))
    else:
        score = cosine_tf(as_bag(on), as_bag(pn))

    if cfg.use_edit_fallback and (len(o) < 50 or score < 0.5):
        score = max(score, levenshtein_ratio(o, p))

    return max(0.0, min(1.0, score))

