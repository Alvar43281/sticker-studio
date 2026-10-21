import sys, numpy as np, cv2
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import render_frames, encode_gif, add_text

root = Path(r"D:\agent\poster-studio")
rgba = np.array(Image.open(root/"clean_static.png").convert("RGBA"))
jobs = [
    ("jelly",  "果冻", dict(glow=True)),
    ("glow",   "流光", dict(glow=True)),
    ("trail",  "残影", dict(glow=False, trail=True)),
    ("burst",  "崩解", dict(glow=True)),
]
for fn, preset, kw in jobs:
    fr = render_frames(rgba, preset, n=24, bg=(255,255,255), **kw)
    p = encode_gif(fr, str(root/f"fx_{fn}.gif"))
    print(preset, "→", p.name, "%.0f KB"%(p.stat().st_size/1024))
# 抽帧做对照
sheet = Image.new("RGB",(4*220,220),(255,255,255))
for i,(fn,preset,kw) in enumerate(jobs):
    fr = render_frames(rgba, preset, n=24, bg=(255,255,255), **kw)
    sheet.paste(Image.fromarray(fr[8]).resize((220,220)), (i*220,0))
sheet.save(root/"fx_sheet.png")
print("ok")
