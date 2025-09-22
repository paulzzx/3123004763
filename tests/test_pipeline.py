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
from src.io_utils import read_text  # 新增：用于覆盖 io_utils 分支


# -----------------------
# 基础功能与单位函数测试
# -----------------------

def test_normalize_basic():
    # 基本规范化：去掉符号和换行
    assert normalize("天气，晴！\n") == "天气晴"


def test_char_ngrams_short_and_empty():
    # 输入过短时：直接返回原串
    assert char_ngrams("ab", 3) == ["ab"]
    # 空字符串：应返回空列表
    assert char_ngrams("", 3) == []


def test_similarity_jaccard_overlap():
    # Jaccard 相似度：集合交并情况
    a = as_set(["abc", "bcd", "cde"])
    b = as_set(["abc", "bcx", "cxy"])
    s = jaccard(a, b)
    assert 0.0 <= s <= 1.0
    assert isinstance(s, float)


def test_cosine_tf_bag():
    # Cosine 相似度：基于 bag 的频率向量
    a = as_bag(["a", "a", "b"])  # 2 个 "a"
    b = as_bag(["a", "b", "b"])  # 2 个 "b"
    c = cosine_tf(a, b)
    assert 0.0 <= c <= 1.0


def test_levenshtein_ratio_known_case():
    # 经典例子：kitten → sitting (3 编辑步，长度 7)
    expected = 1 - 3 / 7
    assert levenshtein_ratio("kitten", "sitting") == pytest.approx(expected, rel=1e-6)


# -----------------------
# pipeline 主流程测试
# -----------------------

def test_pipeline_chinese_example():
    # 中文示例：检查主流程能跑通
    orig = "今天是星期天，天气晴，今天晚上我要去看电影。"
    plag = "今天是周天，天气晴朗，我晚上要去看电影。"
    cfg = Config(n=3, method="jaccard")
    s = compute_similarity(orig, plag, cfg)
    assert 0.0 <= s <= 1.0


def test_pipeline_empty_files():
    # 空文本：完全相似 / 完全不相似
    cfg = Config()
    assert compute_similarity("", "", cfg) == 1.0
    assert compute_similarity("hello", "", cfg) == 0.0


def test_pipeline_english_texts():
    # 英文示例：正常相似度计算
    a = "Natural Language Processing is fun."
    b = "NLP is truly fun and useful!"
    s = compute_similarity(a, b, Config(n=3))
    assert 0.0 <= s <= 1.0


def test_synonyms_extension_improves_similarity():
    # 检查同义词替换能提升相似度
    orig = "今天是星期天，天气晴，今天晚上我要去看电影。"
    plag = "今天是周天，天气晴朗，我晚上要去看电影。"
    synonyms = {"星期天": "周天", "天气晴": "天气晴朗", "今天晚上": "我晚上"}
    s1 = compute_similarity(orig, plag, Config(n=3, use_synonyms=False))
    s2 = compute_similarity(orig, plag, Config(n=3, use_synonyms=True, synonyms=synonyms))
    assert s2 >= s1


def test_edit_fallback_extension():
    # 检查编辑距离兜底：短文本时能提升相似度
    a, b = "猫", "猫咪"
    s_no = compute_similarity(a, b, Config(n=3, use_edit_fallback=False))
    s_yes = compute_similarity(a, b, Config(n=3, use_edit_fallback=True))
    assert s_yes >= s_no


# -----------------------
# CLI 集成测试
# -----------------------

def test_cli_behavior(tmp_path: Path):
    # 集成测试：直接调用 main.py
    proj_root = Path(__file__).resolve().parents[1]
    main_py = proj_root / "main.py"
    orig = tmp_path / "orig.txt"
    plag = tmp_path / "plag.txt"
    ans = tmp_path / "ans.txt"

    orig.write_text("abc", encoding="utf-8")
    plag.write_text("abd", encoding="utf-8")

    argv_bak = sys.argv[:]
    try:
        # 模拟命令行参数
        sys.argv = [str(main_py), str(orig), str(plag), str(ans)]
        # 捕获 SystemExit，不让 pytest 当成错误
        with pytest.raises(SystemExit) as e:
            runpy.run_path(str(main_py), run_name="__main__")
        # 正常退出码应为 0
        assert e.value.code == 0
    finally:
        sys.argv = argv_bak

    # 输出检查：必须是两位小数的百分比
    out = ans.read_text(encoding="utf-8").strip()
    assert re.fullmatch(r"\d+\.\d{2}", out) is not None
    val = float(out)
    assert 0.0 <= val <= 100.0


def test_pipeline_cosine_branch():
    # 命中 pipeline.py 的 else 分支（cosine 路径）
    a, b = "abc", "abd"
    s = compute_similarity(a, b, Config(method="cosine", n=3))  # 非 jaccard
    assert 0.0 <= s <= 1.0


def test_io_read_text_missing_file(tmp_path):
    # 命中 io_utils.py:6 → FileNotFoundError 分支
    missing = tmp_path / "no_such_file.txt"
    with pytest.raises(FileNotFoundError):
        read_text(missing)


def test_io_read_text_gb18030_fallback(tmp_path):
    # 命中 io_utils.py:9-10 → gb18030 回退分支
    s = "天气晴朗，我晚上要去看电影。"
    p = tmp_path / "gb.txt"
    # 故意用 gb18030 写，触发 UTF-8 解码失败
    p.write_bytes(s.encode("gb18030"))
    assert read_text(p) == s
