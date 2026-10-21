import io, re
p = r"D:\agent\poster-studio\sticker.py"
t = io.open(p, encoding="utf-8").read()

# 去掉之前插入的简易定义
t = re.sub(r'from pathlib import Path as _P\nimport os as _os\nSEG_MODEL = _os\.environ\.get\(\n?.*?\n\)\n',
           '', t, flags=re.S)
t = re.sub(r'from pathlib import Path as _P\nimport os as _os\nSEG_MODEL = .*?\n',
           '', t, flags=re.S)

block = '''from pathlib import Path as _P
import os as _os


def _resolve_seg_model() -> str:
    """按优先级找分割模型：环境变量 > 脚本同级 models > 上级 models > 旧路径。"""
    env = _os.environ.get("SEG_MODEL_PATH")
    if env and _P(env).exists():
        return env
    here = _P(__file__).resolve().parent
    for cand in (
        here / "models" / "isnetis.onnx",
        here.parent / "models" / "isnetis.onnx",
        _P(r"D:\\agent\\sequence-evolver\\models\\isnetis.onnx"),
    ):
        if cand.exists():
            return str(cand)
    return str(here / "models" / "isnetis.onnx")


SEG_MODEL = _resolve_seg_model()

'''
# 插到 FONT_BOLD 定义之后
t = t.replace('SEG_MODEL = r"D:\\agent\\sequence-evolver\\models\\isnetis.onnx"\n', block, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("patched")
