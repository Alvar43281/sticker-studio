import sys, numpy as np, cv2
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import trim, make_sticker, add_text

mat = Path(r"D:\agent\素材"); out = Path(r"D:\agent\poster-studio\meme")
im = Image.open(mat/"奶龙_睡觉.png").convert("RGB")
arr = np.asarray(im, np.uint8)
hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV).astype(np.float32)
s = hsv[...,1]/255.0
a = np.clip((s - 0.09)/0.16, 0, 1)
a = cv2.morphologyEx((a>0.4).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9,9),np.uint8)).astype(np.float32)
n, cc, st, _ = cv2.connectedComponentsWithStats((a>0.5).astype(np.uint8), 8)
if n>1:
    keep = 1+int(np.argmax(st[1:, cv2.CC_STAT_AREA])); a = (cc==keep).astype(np.float32)
a = cv2.GaussianBlur(a,(5,5),0)
print("主体占比 %.0f%%" % (100*(a>0.5).mean()))
sub, al = trim(arr, a)
r2, a2 = make_sticker(sub, al, size=512, border="none", border_px=0)
rgba = add_text(np.dstack([r2,(a2*255).astype(np.uint8)]), "奶龙", "困了")
Image.fromarray(rgba,"RGBA").save(out/"plain_nailong_sleep.png")
bg = Image.new("RGBA", (512,512), (255,255,255,255))
Image.alpha_composite(bg, Image.fromarray(rgba,"RGBA")).convert("RGB").save(out/"plain_nailong_sleep_w.png")

# 重建对比图
W=210
sheet = Image.new("RGB",(W*4, W*2),(245,245,248))
for i,k in enumerate(["kangaroo","nailong_happy","nailong_sleep","laugh"]):
    sheet.paste(Image.open(out/f"static_{k}_w.png").resize((W,W)), (i*W,0))
    sheet.paste(Image.open(out/f"plain_{k}_w.png").resize((W,W)), (i*W,W))
sheet.save(out/"border_compare.png")
print("ok")
