from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
A = Path(r"D:\agent\poster-studio\assets")

def checker(size, cell=16):
    im = Image.new("RGB", (size, size), (255,255,255))
    d = ImageDraw.Draw(im)
    for y in range(0, size, cell):
        for x in range(0, size, cell):
            if (x//cell + y//cell) % 2:
                d.rectangle([x, y, x+cell-1, y+cell-1], fill=(226,228,232))
    return im

# 1) 抠图演示：棋盘格 + 透明主体
cut = Image.open(A/"ex_kangaroo.png").convert("RGBA").resize((420,420))
bg = checker(420)
Image.alpha_composite(bg.convert("RGBA"), cut).convert("RGB").save(A/"mod_cutout.png")

# 2) 序列演示：倒计时 3
im = Image.new("RGB",(420,420),(255,255,255)); d = ImageDraw.Draw(im)
d.ellipse([40,40,380,380], fill=(233,90,90))
f = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 210)
tw = d.textlength("3", font=f); d.text(((420-tw)/2, 90), "3", font=f, fill=(255,255,255))
im.save(A/"mod_seq.png")

# 3) 视频演示：取一帧
import cv2
cap = cv2.VideoCapture(r"D:\agent\sequence-evolver\artifacts\focus_anime.mp4")
ok, fr = cap.read(); cap.release()
if ok:
    Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).resize((420,420)).save(A/"mod_video.png")

# 4) 贴纸演示：白底成品
Image.open(A/"ex_kangaroo_w.png").convert("RGB").resize((420,420)).save(A/"mod_sticker.png")
print("模块缩略图 4 张完成")
