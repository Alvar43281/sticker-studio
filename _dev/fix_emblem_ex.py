import sys, numpy as np
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import robust_alpha, trim, make_sticker, encode_webp
from logo import make_logo

A = Path(r"D:\agent\poster-studio\assets"); S = 420
src = np.asarray(Image.open(r"D:\agent\素材\奶龙_开心.png").convert("RGB"), np.uint8)
a = robust_alpha(src); sub, al = trim(src, a)
rgb, alpha = make_sticker(sub, al, size=S, border="none", border_px=0, shadow=False)

fr = make_logo(rgb, alpha, n=48, size=S, mono=False, tint=(120,180,255))
# 选汇聚中后段：既能看到粒子，也能看出形状
for idx, name in [(30, "ex5_emblem.png"), ]:
    Image.fromarray(fr[idx]).save(A/name)
encode_webp(fr, str(A/"ex5_emblem.webp"), fps=20)
print("已重做徽记示例，取第 30 帧")
