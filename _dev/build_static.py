import sys, numpy as np
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import robust_alpha, trim, make_sticker, add_text, render_frames, encode_webp

mat = Path(r"D:\agent\素材"); out = Path(r"D:\agent\poster-studio\meme"); out.mkdir(exist_ok=True)
jobs = [
 ("奶龙_睡觉.png", None, "奶龙", "困了", "呼吸", "nailong_sleep"),
 ("奶龙_开心.png", None, "奶龙", "我来啦", "弹跳", "nailong_happy"),
 ("袋鼠.png", (0,0,610,600), "你的胆子", "肥嘟嘟的", "冲击", "kangaroo"),
 ("哈基米.png", None, "哈基米", "哈基米", "抖动", "hajimi"),
 ("小黄人_大笑.png", None, "哈哈", "笑死我了", "果冻", "laugh"),
]
sheet = Image.new("RGB", (5*220, 220), (240,240,244))
for i,(fname, crop, top, bot, eff, key) in enumerate(jobs):
    im = Image.open(mat/fname).convert("RGBA")
    if crop: im = im.crop(crop)
    if key == "hajimi":
        im = im.resize((im.width*2, im.height*2), Image.LANCZOS)
    arr = np.asarray(im); rgb = arr[..., :3].copy(); al = arr[...,3].astype(np.float32)/255.0
    a = al if al.min() <= 0.98 else robust_alpha(rgb)
    sub, al2 = trim(rgb, a)
    r2, a2 = make_sticker(sub, al2, size=512, border="white", border_px=10)
    rgba = add_text(np.dstack([r2,(a2*255).astype(np.uint8)]), top, bot)
    Image.fromarray(rgba, "RGBA").save(out/f"static_{key}.png")
    # 白底预览
    bgw = np.array(Image.fromarray(rgba).convert("RGB"), np.uint8)
    Image.fromarray(bgw).save(out/f"static_{key}_white.png")
    fr = render_frames(rgba, eff, n=20, bg=(255,255,255))
    encode_webp(fr, str(out/f"real_{key}.webp"), fps=12)
    sheet.paste(Image.fromarray(bgw).resize((220,220)), (i*220,0))
    print(f"{fname} → static_{key}.png")
sheet.save(out/"static_sheet.png")
print("ok")
