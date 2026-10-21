import sys, numpy as np
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import robust_alpha, trim, make_sticker, render_frames, encode_webp
from extra import rot_float_frames
from fx import FRAME_FX

root = Path(r"D:\agent\poster-studio"); A = root/"assets"
src = np.asarray(Image.open(root/"src_clean.png").convert("RGB"), np.uint8)
a = robust_alpha(src); sub, al = trim(src, a)
r2, a2 = make_sticker(sub, al, size=320, border="none", border_px=0)
rgba = np.dstack([r2, (a2*255).astype(np.uint8)])
bg = (255,255,255)
a4 = rgba[...,3:4].astype(np.float32)/255.0
base = (rgba[...,:3].astype(np.float32)*a4 + np.array(bg,np.float32)*(1-a4)).astype(np.uint8)

subject = [("shake","抖动"),("bounce","弹跳"),("punch","冲击"),("wobble","摇摆"),
           ("breathe","呼吸"),("jelly","果冻"),("glow","流光"),("trail","残影"),("burst","崩解")]
for key, cn in subject:
    kw = {"glow":True} if cn=="流光" else ({"trail":True} if cn=="残影" else ({"glow":True} if cn=="崩解" else {}))
    fr = render_frames(rgba, cn, n=20, bg=bg, **kw)
    encode_webp(fr, str(A/f"fx_{key}.webp"), fps=12)
print("主体类 9 个 ok")

fr = rot_float_frames(rgba, n=24, bg=bg)
encode_webp(fr, str(A/"fx_rotate.webp"), fps=12)
print("旋转悬浮 ok")

frame_map = [("kenburns","肯·伯恩斯"),("wave","波浪扭曲"),("glitch","故障"),
             ("bokeh","光斑漂移"),("kaleido","万花筒"),("polar","极坐标展开"),
             ("crt","CRT"),("halftone","半调网点"),("oldfilm","老电影")]
for key, cn in frame_map:
    fr = FRAME_FX[cn](base, n=20)
    encode_webp(fr, str(A/f"fx_{key}.webp"), fps=12)
print("画面类 9 个 ok")

tot = sum(f.stat().st_size for f in A.iterdir() if f.suffix=='.webp')
print("webp 素材共 %.1f MB" % (tot/1024/1024))
