import sys, numpy as np, cv2
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import trim, make_sticker, encode_gif, encode_webp
from extra import rot_float_frames

out = Path(r"D:\agent\poster-studio\meme")
arr = np.asarray(Image.open(r"D:\agent\素材\鸡块.png").convert("RGB"), np.uint8)
gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY).astype(np.float32)
print("亮度: 背景约", np.percentile(gray, 90), " 主体约", np.percentile(gray, 10))
a = np.clip((205 - gray) / 55.0, 0, 1)          # 低于 205 的算主体
a = cv2.morphologyEx((a>0.45).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7,7),np.uint8)).astype(np.float32)
n, cc, st, _ = cv2.connectedComponentsWithStats((a>0.5).astype(np.uint8), 8)
if n>1:
    keep = 1+int(np.argmax(st[1:, cv2.CC_STAT_AREA])); a = (cc==keep).astype(np.float32)
a = cv2.GaussianBlur(a,(5,5),0)
print("鸡块主体 %.0f%%" % (100*(a>0.5).mean()))
sub, al = trim(arr, a)
r2, a2 = make_sticker(sub, al, size=384, border="none", border_px=0, shadow=False)
rgba = np.dstack([r2, (a2*255).astype(np.uint8)])
Image.fromarray(rgba,"RGBA").save(out/"nugget.png")
fr = rot_float_frames(rgba, n=24, bg=(255,255,255))
encode_gif(fr, str(out/"nugget_spin.gif"), fps=12)
encode_webp(fr, str(out/"nugget_spin.webp"), fps=12)
print("旋转 GIF 完成")
# 抽 3 帧看
sheet = Image.new("RGB",(3*220,220),(245,245,248))
for i,k in enumerate([2,8,16]):
    sheet.paste(Image.fromarray(fr[k]).resize((220,220)), (i*220,0))
sheet.save(out/"nugget_sheet.png")
print("ok")
