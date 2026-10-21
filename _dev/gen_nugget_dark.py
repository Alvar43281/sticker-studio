import sys, numpy as np, cv2
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import trim, make_sticker, encode_webp
from extra import rot_float_frames

A = Path(r"D:\agent\poster-studio\assets")
arr = np.asarray(Image.open(r"D:\agent\素材\鸡块.png").convert("RGB"), np.uint8)
gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY).astype(np.float32)
a = np.clip((205 - gray) / 55.0, 0, 1)
a = cv2.morphologyEx((a>0.45).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7,7),np.uint8)).astype(np.float32)
n, cc, st, _ = cv2.connectedComponentsWithStats((a>0.5).astype(np.uint8), 8)
if n>1:
    keep = 1+int(np.argmax(st[1:, cv2.CC_STAT_AREA])); a = (cc==keep).astype(np.float32)
a = cv2.GaussianBlur(a,(5,5),0)
sub, al = trim(arr, a)
r2, a2 = make_sticker(sub, al, size=360, border="none", border_px=0, shadow=False)
rgba = np.dstack([r2, (a2*255).astype(np.uint8)])

DARK = (11, 12, 16)          # 与网页 --bg 一致
fr = rot_float_frames(rgba, n=24, bg=DARK, shadow_rgb=(110, 160, 255), shadow_alpha=70)
encode_webp(fr, str(A/"nugget_spin.webp"), fps=12)
Image.fromarray(fr[6]).save(A/"nugget_frame.png")
print("深色底版本已生成", (A/'nugget_spin.webp').stat().st_size//1024, "KB")
