from collections import Counter
from math import sqrt

def jaccard(a:set,b:set)->float:
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    return len(a & b)/len(a | b)

def cosine_tf(a:Counter,b:Counter)->float:
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    dot=sum(a[k]*b.get(k,0) for k in a)
    na=sqrt(sum(v*v for v in a.values()))
    nb=sqrt(sum(v*v for v in b.values()))
    return dot/(na*nb) if na*nb!=0 else 0.0

def levenshtein_ratio(s1:str,s2:str)->float:
    if not s1 and not s2: return 1.0
    if not s1 or not s2: return 0.0
    if len(s1)<len(s2): s1,s2=s2,s1
    prev=list(range(len(s2)+1))
    for i,c1 in enumerate(s1,1):
        curr=[i]
        for j,c2 in enumerate(s2,1):
            ins=curr[j-1]+1; dele=prev[j]+1; sub=prev[j-1]+(c1!=c2)
            curr.append(min(ins,dele,sub))
        prev=curr
    dist=prev[-1]
    return 1-dist/max(len(s1),len(s2))
