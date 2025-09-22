from collections import Counter
from math import sqrt

# Jaccard 相似度：基于集合交并比
def jaccard(a: set, b: set) -> float:
    if not a and not b: 
        return 1.0   # 两个集合都空 → 完全相似
    if not a or not b: 
        return 0.0   # 其中一个空 → 完全不相似
    return len(a & b) / len(a | b)

# 余弦相似度（基于 term frequency）
def cosine_tf(a: Counter, b: Counter) -> float:
    if not a and not b: 
        return 1.0
    if not a or not b: 
        return 0.0
    # 点积：共同 token 的频次相乘
    dot = sum(a[k] * b.get(k, 0) for k in a)
    # 向量长度（L2 norm）
    na = sqrt(sum(v * v for v in a.values()))
    nb = sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na * nb != 0 else 0.0

# Levenshtein 编辑距离 → 相似度比例
def levenshtein_ratio(s1: str, s2: str) -> float:
    if not s1 and not s2: 
        return 1.0
    if not s1 or not s2: 
        return 0.0
    # 确保 s1 是较长的那个，减少循环次数
    if len(s1) < len(s2): 
        s1, s2 = s2, s1
    # 动态规划：只保留上一行，节省空间
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1, 1):
        curr = [i]
        for j, c2 in enumerate(s2, 1):
            ins = curr[j - 1] + 1      # 插入
            dele = prev[j] + 1         # 删除
            sub = prev[j - 1] + (c1 != c2)  # 替换（相同为0，不同为1）
            curr.append(min(ins, dele, sub))
        prev = curr
    dist = prev[-1]
    # 相似度 = 1 - (编辑距离 / 最大长度)
    return 1 - dist / max(len(s1), len(s2))
