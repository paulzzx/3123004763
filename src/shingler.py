from collections import Counter
from typing import Iterable, Set

def as_set(it: Iterable[str]) -> Set[str]:
    return set(it)

def as_bag(it: Iterable[str]) -> Counter:
    return Counter(it)
