import sys, time, numpy as np, cv2, torch
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\sequence-evolver")
sys.path.insert(0, r"D:\agent\poster-studio")
from core import Engine
from sticker import cutout, trim, make_sticker, add_text, render_frames, encode_gif

root = Path(r"D:\agent\poster-studio")
e = Engine(r"D:\agent\sequence-evolver\models\sd15-fp16")
img = e.pipe(prompt="anime girl smiling, upper body, plain light grey background, cel shading, clean lines",
             negative_prompt="text, watermark, busy background, scenery",
             num_inference_steps=26, guidance_scale=7.5,
             generator=e._generator(7)).images[0]
img.save(root/"src_clean.png")
src = np.asarray(img, np.uint8)
a = cutout(src); print("alpha mean %.2f" % a.mean())
im, al = trim(src, a)
rgba, alpha = make_sticker(im, al, size=512, border="white", border_px=10)
rgba8 = add_text(np.dstack([rgba,(alpha*255).astype(np.uint8)]), "打工吧", "今天也是")
Image.fromarray(rgba8).save(root/"clean_static.png")
for name, preset in [("shake","抖动"),("bounce","弹跳"),("punch","冲击")]:
    fr = render_frames(rgba8, preset, n=24, bg=(255,255,255))
    p = encode_gif(fr, str(root/f"clean_{name}.gif"))
    print(preset, p.name, "%.0f KB"%(p.stat().st_size/1024))
