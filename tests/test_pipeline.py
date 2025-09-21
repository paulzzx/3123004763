from pathlib import Path
import re
import runpy
import sys
import pytest

from src.pipeline import Config, compute_similarity
from src.normalizer import normalize
from src.similarity import jaccard, cosine_tf, levenshtein_ratio
from src.tokenizer import char_ngrams
from src.shingler import as_set, as_bag


def test_normalize_basic():
    assert normalize("天气，晴！\n") == "天气晴"


def test_char_ngrams_short_and_empty():
    assert char_ngrams("ab", 3) == ["ab"]
    assert char_ngrams("", 3) == []


def test_similarity_jaccard_overlap():
    a = as_set(["abc", "bcd", "cde"])
    b = as_set(["abc", "bcx", "cxy"])
    s = jaccard(a, b)
    assert 0.0 <= s <= 1.0
    assert isinstance(s, float)


def test_cosine_tf_bag():
    a = as_bag(["a", "a", "b"])  # 2 a's
    b = as_bag(["a", "b", "b"])  # 2 b's
    c = cosine_tf(a, b)
    assert 0.0 <= c <= 1.0


def test_levenshtein_ratio_known_case():
    # kitten -> sitting (3 edits, length 7)
    expected = 1 - 3 / 7
    assert levenshtein_ratio("kitten", "sitting") == pytest.approx(expected, rel=1e-6)


def test_pipeline_chinese_example():
    orig = "今天是星期天，天气晴，今天晚上我要去看电影。"
    plag = "今天是周天，天气晴朗，我晚上要去看电影。"
    cfg = Config(n=3, method="jaccard")
    s = compute_similarity(orig, plag, cfg)
    assert 0.0 <= s <= 1.0


def test_pipeline_empty_files():
    cfg = Config()
    assert compute_similarity("", "", cfg) == 1.0
    assert compute_similarity("hello", "", cfg) == 0.0


def test_pipeline_english_texts():
    a = "Natural Language Processing is fun."
    b = "NLP is truly fun and useful!"
    s = compute_similarity(a, b, Config(n=3))
    assert 0.0 <= s <= 1.0


def test_synonyms_extension_improves_similarity():
    orig = "今天是星期天，天气晴，今天晚上我要去看电影。"
    plag = "今天是周天，天气晴朗，我晚上要去看电影。"
    synonyms = {"星期天": "周天", "天气晴": "天气晴朗", "今天晚上": "我晚上"}
    s1 = compute_similarity(orig, plag, Config(n=3, use_synonyms=False))
    s2 = compute_similarity(orig, plag, Config(n=3, use_synonyms=True, synonyms=synonyms))
    assert s2 >= s1


def test_edit_fallback_extension():
    a, b = "猫", "猫咪"
    s_no = compute_similarity(a, b, Config(n=3, use_edit_fallback=False))
    s_yes = compute_similarity(a, b, Config(n=3, use_edit_fallback=True))
    assert s_yes >= s_no


import contextlib

def test_cli_behavior(tmp_path: Path):
    proj_root = Path(__file__).resolve().parents[1]
    main_py = proj_root / "main.py"
    orig = tmp_path / "orig.txt"
    plag = tmp_path / "plag.txt"
    ans = tmp_path / "ans.txt"

    orig.write_text("abc", encoding="utf-8")
    plag.write_text("abd", encoding="utf-8")

    argv_bak = sys.argv[:]
    try:
        sys.argv = [str(main_py), str(orig), str(plag), str(ans)]
        # 捕获 SystemExit，不让 pytest 当成错误
        with pytest.raises(SystemExit) as e:
            runpy.run_path(str(main_py), run_name="__main__")
        # 退出码必须是 0（正常）
        assert e.value.code == 0
    finally:
        sys.argv = argv_bak

    out = ans.read_text(encoding="utf-8").strip()
    assert re.fullmatch(r"\d+\.\d{2}", out) is not None
    val = float(out)
    assert 0.0 <= val <= 100.0