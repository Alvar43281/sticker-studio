import sys, numpy as np, cv2
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import cutout, trim, make_sticker, add_text, render_frames, encode_gif, encode_webp

root = Path(r"D:\agent\poster-studio")
src = np.asarray(Image.open(root/"src_clean.png").convert("RGB"), np.uint8)
a = cutout(src); sub, al = trim(src, a)
rgb, alpha = make_sticker(sub, al, size=448, border="white", border_px=9)
rgba = np.dstack([rgb,(alpha*255).astype(np.uint8)])
rgba = add_text(rgba, "打工吧", "今天也是")

for name, preset, kw in [("jelly","果冻",{}), ("shake","抖动",{}), ("glow","流光",dict(glow=True))]:
    fr = render_frames(rgba, preset, n=20, bg=(255,255,255), **kw)
    g = encode_gif(fr, str(root/f"v2_{name}.gif"), fps=12)
    w = encode_webp(fr, str(root/f"v2_{name}.webp"), fps=12)
    print(f"{preset}: GIF {g.stat().st_size/1024:.0f}KB  WebP {w.stat().st_size/1024:.0f}KB")
Image.fromarray(fr[6]).save(root/"v2_frame.png")
print("ok")
