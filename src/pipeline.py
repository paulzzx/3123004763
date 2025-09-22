from dataclasses import dataclass
from typing import Dict, Optional
from .normalizer import normalize, apply_synonyms
from .tokenizer import char_ngrams
from .shingler import as_set, as_bag
from .similarity import jaccard, cosine_tf, levenshtein_ratio

# 配置对象，用来控制相似度计算的参数
@dataclass(frozen=True)
class Config:
    n: int = 3                       # n-gram 的长度
    method: str = "jaccard"          # 相似度计算方法（jaccard / cosine）
    use_synonyms: bool = False       # 是否启用同义词替换
    synonyms: Optional[Dict[str, str]] = None  # 同义词词典
    use_edit_fallback: bool = False  # 是否启用编辑距离作为兜底

# 计算两段文本的相似度
def compute_similarity(orig: str, plag: str, cfg: Config) -> float:
    # 如果开启了同义词替换，先做文本预处理
    if cfg.use_synonyms and cfg.synonyms:
        orig = apply_synonyms(orig, cfg.synonyms)
        plag = apply_synonyms(plag, cfg.synonyms)

    # 基础规范化：统一大小写、去掉无关符号等
    o = normalize(orig)
    p = normalize(plag)

    # 转换为 n-gram 序列
    on = char_ngrams(o, cfg.n)
    pn = char_ngrams(p, cfg.n)

    # 主方法：jaccard 或 cosine
    if cfg.method == "jaccard":
        score = jaccard(as_set(on), as_set(pn))
    else:
        score = cosine_tf(as_bag(on), as_bag(pn))

    # 兜底：短文本或相似度过低时，尝试编辑距离提升鲁棒性
    if cfg.use_edit_fallback and (len(o) < 50 or score < 0.5):
        score = max(score, levenshtein_ratio(o, p))

    # 保证结果在 [0, 1] 区间内
    return max(0.0, min(1.0, score))


