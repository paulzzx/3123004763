import unicodedata, re, string
from typing import Dict

_ASCII_PUNCTS = set(string.punctuation)
_ZH_PUNCTS = set(["，","。","！","？","；","：","、","“","”","‘","’","（","）","《","》","【","】","—","…","·"])
_PUNCT_TABLE = str.maketrans({c: " " for c in (_ASCII_PUNCTS | _ZH_PUNCTS)})

def normalize(text: str) -> str:
    t = unicodedata.normalize("NFKC", text).casefold()
    t = t.translate(_PUNCT_TABLE)
    t = re.sub(r"\s+", "", t)
    return t

def apply_synonyms(text: str, mapping: Dict[str,str]) -> str:
    for k,v in sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True):
        text = text.replace(k, v)
    return text
