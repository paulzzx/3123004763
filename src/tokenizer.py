from typing import List

def char_ngrams(text: str, n: int = 3) -> List[str]:
    """按字符生成 n-gram"""
    if not text:
        return []
    if len(text) < n:
        return [text]
    return [text[i:i+n] for i in range(len(text) - n + 1)]

