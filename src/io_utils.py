from pathlib import Path

# 读取文本文件，自动处理常见编码问题
def read_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        # 文件不存在时直接抛异常，方便调用方捕获
        raise FileNotFoundError(f"File not found: {path}")
    try:
        # 优先按 UTF-8 读取
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # 部分 Windows/旧文件用 gb18030，做个兼容
        return p.read_text(encoding="gb18030")

# 写入文本文件，确保父目录存在
def write_text(path: str, content: str) -> None:
    p = Path(path)
    # 自动创建多级目录，避免因目录缺失报错
    p.parent.mkdir(parents=True, exist_ok=True)
    # 统一写成 UTF-8，保证跨平台一致性
    p.write_text(content, encoding="utf-8")

