import unicodedata
import string
from typing import Dict

_ASCII_PUNCTS = set(string.punctuation)
_ZH_PUNCTS = set([
    "，","。","！","？","；","：","、","“","”","‘","’",
    "（","）","《","》","【","】","—","…","·"
])
_PUNCT_TABLE = str.maketrans({c: " " for c in (_ASCII_PUNCTS | _ZH_PUNCTS)})

def normalize(text: str) -> str:
    """标准化文本：Unicode 归一化、大小写折叠、去标点、去空白"""
    t = unicodedata.normalize("NFKC", text).casefold()
    t = t.translate(_PUNCT_TABLE)
    # 用内建字符串方法替换正则，去掉所有空白字符
    t = t.replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", "")
    return t

def apply_synonyms(text: str, mapping: Dict[str, str]) -> str:
    """应用同义词替换，优先匹配长词"""
    for k, v in sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True):
        text = text.replace(k, v)
    return text
