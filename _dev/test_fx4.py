import sys, numpy as np
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from fx import FRAME_FX
from sticker import encode_gif, encode_webp

out = Path(r"D:\agent\poster-studio\out")
img = np.asarray(Image.open(r"D:\agent\poster-studio\meme\src_cat.png").convert("RGB").resize((448,448)), np.uint8)
names = ["极坐标展开","CRT","半调网点","老电影"]
sheet = Image.new("RGB", (4*200, 200), (240,240,244))
for i, nm in enumerate(names):
    fr = FRAME_FX[nm](img, n=24)
    encode_gif(fr, str(out/f"fx2_{i}.gif"), fps=12)
    encode_webp(fr, str(out/f"fx2_{i}.webp"), fps=12)
    sheet.paste(Image.fromarray(fr[8]).resize((200,200)), (i*200,0))
    print(nm, "ok")
sheet.save(out/"fx2_sheet.png")
print("done")
