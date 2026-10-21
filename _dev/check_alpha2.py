from PIL import Image
import numpy as np
from pathlib import Path
A = Path(r"D:\agent\poster-studio\assets")
im = Image.open(A/"nugget_spin.webp")
print("总帧", im.n_frames)
for idx in (0, 12):
    im.seek(idx)
    f = np.array(im.convert("RGBA"))
    print(f"帧{idx}: 角落 alpha={f[5,5,3]}, 中心 alpha={f[170,170,3]}, 最大 alpha={f[...,3].max()}")
    # 合成到棋盘格上看得清透明
    sz = f.shape[0]
    chk = Image.new("RGB",(sz,sz),(255,255,255))
    from PIL import ImageDraw
    d = ImageDraw.Draw(chk); cell=20
    for y in range(0,sz,cell):
        for x in range(0,sz,cell):
            if (x//cell+y//cell)%2: d.rectangle([x,y,x+cell-1,y+cell-1], fill=(210,214,220))
    Image.alpha_composite(chk.convert("RGBA"), Image.fromarray(f)).convert("RGB").save(A/f"nugget_chk_{idx}.png")
print("done")
