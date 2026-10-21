import sys, numpy as np, cv2
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import cutout, trim, make_sticker, add_text, render_frames, encode_gif, encode_webp
from logo import alpha_for_emblem, make_logo

root = Path(r"D:\agent\poster-studio")
assets = root/"assets"; assets.mkdir(exist_ok=True)

# 贴纸素材
src = np.asarray(Image.open(root/"src_clean.png").convert("RGB"), np.uint8)
a = cutout(src); sub, al = trim(src, a)
rgb, alpha = make_sticker(sub, al, size=448, border="white", border_px=9)
rgba = add_text(np.dstack([rgb,(alpha*255).astype(np.uint8)]), "打工吧", "今天也是")

EFF = {"shake":("抖动",{}), "bounce":("弹跳",{}), "punch":("冲击",{}),
       "wobble":("摇摆",{}), "breathe":("呼吸",{}), "jelly":("果冻",{}),
       "glow":("流光",dict(glow=True)), "trail":("残影",dict(trail=True)),
       "burst":("崩解",dict(glow=True))}
for fn,(cn,kw) in EFF.items():
    fr = render_frames(rgba, cn, n=20, bg=(255,255,255), **kw)
    encode_webp(fr, str(assets/f"fx_{fn}.webp"), fps=12)
    print("贴纸", cn, "ok")
Image.fromarray(fr[6]).save(assets/"sticker_still.png")

# 徽记素材
sig = cv2.cvtColor(cv2.imread(r"D:\agent\sequence-evolver\demo_sigil.png"), cv2.COLOR_BGR2RGB)
a2 = alpha_for_emblem(sig); s2, al2 = trim(sig, a2, pad_ratio=0.02)
rgb2, alpha2 = make_sticker(s2, al2, size=448, border="none", border_px=0, shadow=False)
fr2 = make_logo(rgb2, alpha2, n=60, size=448)
encode_webp(fr2, str(assets/"emblem.webp"), fps=20)
Image.fromarray(fr2[52]).save(assets/"emblem_still.png")
print("徽记 ok")

tot = sum(f.stat().st_size for f in assets.iterdir())
print("素材总量 %.1f MB" % (tot/1024/1024))
