import sys, numpy as np
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
import importlib, sticker
importlib.reload(sticker)
from sticker import robust_alpha, trim, make_sticker, add_text, render_frames, encode_webp

mat = Path(r"D:\agent\素材"); out = Path(r"D:\agent\poster-studio\meme"); out.mkdir(exist_ok=True)
jobs = [
 ("奶龙_睡觉.png", None, "奶龙", "困了", "呼吸", "nailong_sleep"),
 ("奶龙_开心.png", None, "奶龙", "我来啦", "弹跳", "nailong_happy"),
 ("袋鼠.png", (0,0,610,600), "你的胆子", "肥嘟嘟的", "冲击", "kangaroo"),
 ("哈基米.png", None, "哈基米", "哈基米", "抖动", "hajimi"),
 ("小黄人_大笑.png", None, "哈哈", "笑死我了", "果冻", "laugh"),
]
for fname, crop, top, bot, eff, key in jobs:
    im = Image.open(mat/fname).convert("RGBA")
    if crop: im = im.crop(crop)
    arr = np.asarray(im); rgb = arr[..., :3].copy(); al = arr[...,3].astype(np.float32)/255.0
    if al.min() > 0.98:
        a = robust_alpha(rgb)
    else:
        a = al
    cov = float((a>0.5).mean())
    sub, al2 = trim(rgb, a)
    r2, a2 = make_sticker(sub, al2, size=448, border="white", border_px=9)
    rgba = add_text(np.dstack([r2,(a2*255).astype(np.uint8)]), top, bot)
    fr = render_frames(rgba, eff, n=20, bg=(255,255,255))
    encode_webp(fr, str(out/f"real_{key}.webp"), fps=12)
    Image.fromarray(fr[6]).save(out/f"real_{key}.png")
    print(f"{fname}: {cov*100:.0f}%  {eff}  {top}/{bot}")
