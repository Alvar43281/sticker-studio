import sys, numpy as np, cv2
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import trim, make_sticker, add_text

mat = Path(r"D:\agent\素材"); out = Path(r"D:\agent\poster-studio\meme")

# --- 1) 睡觉奶龙：棋盘格背景按"饱和度"分离（背景中性色，主体黄）---
im = Image.open(mat/"奶龙_睡觉.png").convert("RGB")
arr = np.asarray(im, np.uint8)
hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
s = hsv[...,1]/255.0; v = hsv[...,2]/255.0
a = np.clip((s - 0.09) / 0.16, 0, 1)
a = cv2.morphologyEx((a>0.4).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9,9),np.uint8)).astype(np.float32)
n, cc, st, _ = cv2.connectedComponentsWithStats((a>0.5).astype(np.uint8), 8)
if n>1:
    keep = 1+int(np.argmax(st[1:, cv2.CC_STAT_AREA])); a = (cc==keep).astype(np.float32)
a = cv2.GaussianBlur(a,(5,5),0)
print("睡觉奶龙 主体占比 %.0f%%" % (100*(a>0.5).mean()))
sub, al = trim(arr, a)
r2, a2 = make_sticker(sub, al, size=512, border="white", border_px=10)
rgba = add_text(np.dstack([r2,(a2*255).astype(np.uint8)]), "奶龙", "困了")
Image.fromarray(rgba,"RGBA").save(out/"static_nailong_sleep.png")
Image.fromarray(np.array(Image.fromarray(rgba).convert("RGB"))).save(out/"static_nailong_sleep_white.png")

# --- 2) 哈基米：整图加白框（不抠图）---
im2 = Image.open(mat/"哈基米.png").convert("RGB")
im2 = im2.resize((int(im2.width*1.6), int(im2.height*1.6)), Image.LANCZOS)
W = 512
inner = 400
im2 = im2.resize((inner, inner), Image.LANCZOS)
canvas = Image.new("RGBA", (W, W), (0,0,0,0))
d = ImageDraw.Draw(canvas)
d.rounded_rectangle([(W-inner)//2-10, (W-inner)//2-10, (W+inner)//2+10, (W+inner)//2+10],
                    radius=26, fill=(255,255,255,255))
mask = Image.new("L", (inner,inner), 0)
ImageDraw.Draw(mask).rounded_rectangle([0,0,inner,inner], radius=18, fill=255)
canvas.paste(im2, ((W-inner)//2, (W-inner)//2), mask)
rgba2 = add_text(np.array(canvas), "哈基米", "哈基米")
Image.fromarray(rgba2,"RGBA").save(out/"static_hajimi.png")
Image.fromarray(np.array(Image.fromarray(rgba2).convert("RGB"))).save(out/"static_hajimi_white.png")
print("哈基米 白框版 ok")

sheet = Image.new("RGB",(5*220,220),(240,240,244))
for i,k in enumerate(["nailong_sleep","nailong_happy","kangaroo","hajimi","laugh"]):
    sheet.paste(Image.open(out/f"static_{k}_white.png").resize((220,220)), (i*220,0))
sheet.save(out/"static_sheet.png")
print("ok")
