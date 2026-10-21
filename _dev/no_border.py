import sys, numpy as np, cv2
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import robust_alpha, trim, make_sticker, add_text

mat = Path(r"D:\agent\素材"); out = Path(r"D:\agent\poster-studio\meme")
jobs = [
 ("奶龙_睡觉.png", None, "奶龙", "困了", "nailong_sleep"),
 ("奶龙_开心.png", None, "奶龙", "我来啦", "nailong_happy"),
 ("袋鼠.png", (0,0,610,600), "你的胆子", "肥嘟嘟的", "kangaroo"),
 ("小黄人_大笑.png", None, "哈哈", "笑死我了", "laugh"),
]
for fname, crop, top, bot, key in jobs:
    im = Image.open(mat/fname).convert("RGBA")
    if crop: im = im.crop(crop)
    arr = np.asarray(im); rgb = arr[..., :3].copy(); al = arr[...,3].astype(np.float32)/255.0
    if al.min() > 0.98:
        a = robust_alpha(rgb)
    else:
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
        s = hsv[...,1]/255.0
        a = np.clip((s-0.09)/0.16, 0, 1)
        a = cv2.morphologyEx((a>0.4).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9,9),np.uint8)).astype(np.float32)
        n, cc, st, _ = cv2.connectedComponentsWithStats((a>0.5).astype(np.uint8), 8)
        if n>1:
            keep = 1+int(np.argmax(st[1:, cv2.CC_STAT_AREA])); a = (cc==keep).astype(np.float32)
        a = cv2.GaussianBlur(a,(5,5),0)
    sub, al2 = trim(rgb, a)
    r2, a2 = make_sticker(sub, al2, size=512, border="none", border_px=0)
    rgba = add_text(np.dstack([r2,(a2*255).astype(np.uint8)]), top, bot)
    Image.fromarray(rgba,"RGBA").save(out/f"plain_{key}.png")
    Image.fromarray(np.array(Image.fromarray(rgba).convert("RGB"))).save(out/f"plain_{key}_w.png")
    print("无白边:", key)

# 对比图：上排白边 / 下排无白边
W=210
sheet = Image.new("RGB",(W*4, W*2),(245,245,248))
for i,k in enumerate(["kangaroo","nailong_happy","nailong_sleep","laugh"]):
    sheet.paste(Image.open(out/f"static_{k}_white.png").resize((W,W)), (i*W,0))
    sheet.paste(Image.open(out/f"plain_{k}_w.png").resize((W,W)), (i*W,W))
sheet.save(out/"border_compare.png")
print("对比图 ok")
