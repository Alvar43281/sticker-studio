import io
p = r"D:\agent\poster-studio\sticker.py"
t = io.open(p, encoding="utf-8").read()

# 1) 通用导入
t = t.replace('from pathlib import Path\nfrom typing import List, Optional, Tuple',
              'import os\nimport shutil\nfrom pathlib import Path\nfrom typing import List, Optional, Tuple')

# 2) FFmpeg / 字体 / 模型 的跨平台解析
old = 'FFMPEG = r"D:\\agent\\tools\\ffmpeg\\bin\\ffmpeg.exe"\nFONT_BOLD = [r"C:\\Windows\\Fonts\\msyhbd.ttc", r"C:\\Windows\\Fonts\\simhei.ttf"]'
new = '''def _find_ffmpeg() -> str:
    env = os.environ.get("FFMPEG_PATH")
    if env and Path(env).exists():
        return env
    for cand in (r"D:\\agent\\tools\\ffmpeg\\bin\\ffmpeg.exe",
                 "/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        if Path(cand).exists():
            return cand
    return shutil.which("ffmpeg") or "ffmpeg"


FONT_BOLD = [
    r"C:\\Windows\\Fonts\\msyhbd.ttc",
    r"C:\\Windows\\Fonts\\simhei.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_REG = [
    r"C:\\Windows\\Fonts\\msyh.ttc",
    r"C:\\Windows\\Fonts\\simhei.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _resolve_seg_model() -> str:
    env = os.environ.get("SEG_MODEL_PATH")
    if env and Path(env).exists():
        return env
    here = Path(__file__).resolve().parent
    for cand in (here / "models" / "isnetis.onnx",
                 here.parent / "models" / "isnetis.onnx",
                 Path(r"D:\\agent\\sequence-evolver\\models\\isnetis.onnx")):
        if cand.exists():
            return str(cand)
    return str(here / "models" / "isnetis.onnx")


FFMPEG = _find_ffmpeg()
SEG_MODEL = _resolve_seg_model()'''
assert old in t
t = t.replace(old, new, 1)

# 3) 字体加载改用 FONT_BOLD（原来已引用，确保存在）
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("sticker.py 跨平台化完成")

# 4) extra.py 的 FFMPEG 同样处理
p2 = r"D:\agent\poster-studio\extra.py"
t2 = io.open(p2, encoding="utf-8").read()
t2 = t2.replace('FFMPEG = r"D:\\agent\\tools\\ffmpeg\\bin\\ffmpeg.exe"',
                'from sticker import FFMPEG')
t2 = t2.replace('FONT_BOLD = [r"C:\\Windows\\Fonts\\msyhbd.ttc", r"C:\\Windows\\Fonts\\simhei.ttf"]',
                'from sticker import FONT_BOLD')
io.open(p2, "w", encoding="utf-8", newline="\n").write(t2)
import ast as _a; _a.parse(t2); print("extra.py 跨平台化完成")
