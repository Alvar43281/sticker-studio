import sys, numpy as np, cv2
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import flat_bg_alpha, auto_cutout, trim, make_sticker, add_text, render_frames, encode_webp

mat = Path(r"D:\agent\素材")
out = Path(r"D:\agent\poster-studio\meme"); out.mkdir(exist_ok=True)

jobs = [
 # 文件, 裁剪(左,上,右,下) or None, 上文字, 下文字, 动效, 说明
 ("奶龙_睡觉.png", None, "奶龙", "困了", "呼吸"),
 ("奶龙_开心.png", None, "奶龙", "我来啦", "弹跳"),
 ("袋鼠.png", (0,0,610,600), "你的胆子", "肥嘟嘟的", "冲击"),
 ("哈基米.png", None, "哈基米", "哈基米", "抖动"),
 ("小黄人_大笑.png", None, "哈哈", "笑死我了", "果冻"),
]
keys = ["nailong_sleep","nailong_happy","kangaroo","hajimi","laugh"]

for (fname, crop, top, bot, eff), key in zip(jobs, keys):
    im = Image.open(mat/fname).convert("RGBA")
    if crop:
        im = im.crop(crop)
    arr = np.asarray(im)
    rgb = arr[..., :3].copy()
    al = arr[..., 3].astype(np.float32) / 255.0
    if al.min() > 0.98:                     # 没有透明信息 → 走平背景抠图
        a = flat_bg_alpha(rgb, tol=34)
        if float((a>0.5).mean()) < 0.08 or float((a>0.5).mean()) > 0.9:
            a = auto_cutout(rgb)
    else:
        a = al
    cov = float((a>0.5).mean())
    sub, al2 = trim(rgb, a)
    st_rgb, st_a = make_sticker(sub, al2, size=448, border="white", border_px=9)
    rgba = add_text(np.dstack([st_rgb,(st_a*255).astype(np.uint8)]), top, bot)
    fr = render_frames(rgba, eff, n=20, bg=(255,255,255))
    encode_webp(fr, str(out/f"real_{key}.webp"), fps=12)
    Image.fromarray(fr[6]).save(out/f"real_{key}.png")
    print(f"{fname}: 主体 {cov*100:.0f}%  动效 {eff}  文字「{top}/{bot}」")
