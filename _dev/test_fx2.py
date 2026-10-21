import sys, numpy as np
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from fx import ken_burns, wave_distort, glitch, bokeh_drift, kaleidoscope
from sticker import encode_gif, encode_webp

out = Path(r"D:\agent\poster-studio\out"); out.mkdir(exist_ok=True)
src = Image.open(r"D:\agent\poster-studio\meme\src_cat.png").convert("RGB").resize((448,448))
img = np.asarray(src, np.uint8)

tests = [("kenburns", ken_burns, {}), ("wave", wave_distort, {}),
         ("glitch", glitch, {}), ("bokeh", bokeh_drift, {}), ("kaleido", kaleidoscope, {})]
sheet = Image.new("RGB", (5*200, 200), (240,240,244))
for i,(name, fn, kw) in enumerate(tests):
    fr = fn(img, n=24, **kw)
    encode_gif(fr, str(out/f"fx_{name}.gif"), fps=12)
    encode_webp(fr, str(out/f"fx_{name}.webp"), fps=12)
    sheet.paste(Image.fromarray(fr[8]).resize((200,200)), (i*200,0))
    print(name, "ok", len(fr), "帧")
sheet.save(out/"fx_sheet.png")
print("done")
