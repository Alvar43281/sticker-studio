import sys, time, numpy as np, cv2
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\sequence-evolver")
sys.path.insert(0, r"D:\agent\poster-studio")
from core import Engine
from sticker import cutout, trim, make_sticker, add_text, render_frames, encode_webp

root = Path(r"D:\agent\poster-studio")
meme = root/"meme"; meme.mkdir(exist_ok=True)
e = Engine(r"D:\agent\sequence-evolver\models\sd15-fp16")

jobs = [
    ("cat",  "cute chubby cartoon cat, big round head, huge eyes, flat colors, thick black outline, plain white background, sticker style, front facing, kawaii",
             "哈基米", "哈基米", "弹跳"),
    ("roo",  "cute cartoon kangaroo, big eyes, simple flat colors, thick outline, plain white background, sticker style, front facing, funny",
             "你的胆子", "肥嘟嘟的", "冲击"),
    ("dino", "cute round cartoon dragon, chubby body, tiny wings, pastel colors, thick outline, plain white background, sticker style, front facing",
             "奶龙", "我来了", "果冻"),
    ("dog",  "cute cartoon puppy, chubby face, simple flat colors, thick outline, plain white background, sticker style, front facing",
             "汪汪", "今天也很棒", "抖动"),
]
for name, prompt, top, bot, eff in jobs:
    t0=time.time()
    img = e.pipe(prompt=prompt, negative_prompt="text, watermark, busy background, realistic photo, multiple characters",
                 num_inference_steps=28, guidance_scale=7.5,
                 generator=e._generator(hash(name) % 1000)).images[0]
    src = np.asarray(img, np.uint8)
    a = cutout(src)
    if float((a>0.4).mean()) < 0.02:
        print(name, "抠图失败"); continue
    sub, al = trim(src, a)
    rgb, alpha = make_sticker(sub, al, size=448, border="white", border_px=9)
    rgba = add_text(np.dstack([rgb,(alpha*255).astype(np.uint8)]), top, bot)
    fr = render_frames(rgba, eff, n=20, bg=(255,255,255), **({} if eff not in ("流光",) else {"glow":True}))
    p = encode_webp(fr, str(meme/f"meme_{name}.webp"), fps=12)
    Image.fromarray(fr[6]).save(meme/f"meme_{name}.png")
    print(f"{name}: {eff}  {p.stat().st_size/1024:.0f}KB  {time.time()-t0:.0f}s")
