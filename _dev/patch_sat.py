import io
p = r"D:\agent\poster-studio\sticker.py"
t = io.open(p, encoding="utf-8").read()
if "def sat_alpha" not in t:
    add = '''

def sat_alpha(img: np.ndarray, s0: float = 0.10, s1: float = 0.26) -> np.ndarray:
    """
    饱和度分离：主体有颜色、背景是中性的灰/白时最有效。
    （很多表情包都是"彩色物体 + 浅灰底"）
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
    s = hsv[..., 1] / 255.0
    a = np.clip((s - s0) / max(s1 - s0, 1e-6), 0, 1)
    a = cv2.morphologyEx((a > 0.4).astype(np.uint8), cv2.MORPH_CLOSE,
                         np.ones((9, 9), np.uint8)).astype(np.float32)
    n, cc, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
    if n > 1:
        keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        a = (cc == keep).astype(np.float32)
    return cv2.GaussianBlur(a, (5, 5), 0)
'''
    t = t.replace("def robust_alpha", add + "\n\ndef robust_alpha", 1)

old = """    a2 = light_bg_alpha(img)
    if good(a2):
        return a2"""
new = """    a_sat = sat_alpha(img)
    if good(a_sat):
        return a_sat

    a2 = light_bg_alpha(img)
    if good(a2):
        return a2"""
if old in t:
    t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("patched sat_alpha")

import sys; sys.path.insert(0, r"D:\agent\poster-studio")
import numpy as np
from PIL import Image
import importlib, sticker; importlib.reload(sticker)
from sticker import robust_alpha, sat_alpha
for name in ["鸡块","奶龙_睡觉","奶龙_开心","袋鼠","哈基米","小黄人_大笑"]:
    arr = np.asarray(Image.open(rf"D:\agent\素材\{name}.png").convert("RGB"), np.uint8)
    print(f"{name:10s} sat {100*(sat_alpha(arr)>0.5).mean():3.0f}%  robust {100*(robust_alpha(arr)>0.5).mean():3.0f}%")
