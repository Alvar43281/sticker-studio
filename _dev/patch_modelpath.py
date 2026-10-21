import io
p = r"D:\agent\poster-studio\sticker.py"
t = io.open(p, encoding="utf-8").read()
old = 'SEG_MODEL = r"D:\\agent\\sequence-evolver\\models\\isnetis.onnx"'
if old in t:
    new = ('from pathlib import Path as _P\n'
           'import os as _os\n'
           'SEG_MODEL = _os.environ.get(\n'
           '    "SEG_MODEL_PATH",\n'
           '    str(_P(__file__).resolve().parent.parent / "models" / "isnetis.onnx"),\n'
           ')')
    t = t.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("SEG_MODEL 改为可配置路径")
else:
    print("未找到旧路径定义，检查：")
    import re
    for line in t.splitlines():
        if "SEG_MODEL" in line: print("  ", line)
