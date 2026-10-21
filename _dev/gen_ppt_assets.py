import sys, numpy as np, cv2
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import robust_alpha, trim, make_sticker, add_text, add_text_at, render_frames, encode_gif, encode_webp
from extra import video_to_gif, sequence_frames

OUT = Path(r"D:\agent\ppt素材")
MAT = Path(r"D:\agent\素材")
S = 400

# ---------- 1) 奶龙 GIF（两种：带字 / 纯图）----------
src = np.asarray(Image.open(MAT/"奶龙_开心.png").convert("RGB"), np.uint8)
a = robust_alpha(src); sub, al = trim(src, a)
r2, a2 = make_sticker(sub, al, size=S, border="white", border_px=8)
plain = np.dstack([r2, (a2*255).astype(np.uint8)])
texted = add_text(plain, "奶龙", "我来啦")

fr = render_frames(plain, "弹跳", n=20, bg=(255,255,255))
encode_gif(fr, str(OUT/"奶龙_弹跳.gif"), fps=12); encode_webp(fr, str(OUT/"奶龙_弹跳.webp"), fps=12)
Image.fromarray(fr[4]).save(OUT/"奶龙_静态.png")

fr2 = render_frames(texted, "果冻", n=20, bg=(255,255,255))
encode_gif(fr2, str(OUT/"奶龙_配文.gif"), fps=12); encode_webp(fr2, str(OUT/"奶龙_配文.webp"), fps=12)
print("奶龙素材 ok")

# ---------- 2) 倒计时 3-2-1 ----------
frames = []
for num, col in (("3",(232,88,88)), ("2",(240,170,60)), ("1",(86,190,120))):
    im = Image.new("RGB",(S,S),(246,247,250)); d = ImageDraw.Draw(im)
    rad = 118
    d.ellipse([S//2-rad, S//2-rad, S//2+rad, S//2+rad], fill=col)
    f = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 150)
    tw = d.textlength(num, font=f)
    d.text(((S-tw)/2, S//2-92), num, font=f, fill=(255,255,255))
    frames.append(im)

cd = sequence_frames(frames, size=S, fps=10, hold=0.6, countdown=False, fade=4)
encode_gif(cd, str(OUT/"倒计时_321.gif"), fps=10); encode_webp(cd, str(OUT/"倒计时_321.webp"), fps=10)
Image.fromarray(cd[2]).save(OUT/"倒计时_静态.png")
print("倒计时 ok，共", len(cd), "帧")

# ---------- 3) MP4 → GIF（用新给的视频）----------
p = video_to_gif(str(OUT/"source_video.mp4"), str(OUT/"视频转GIF.gif"),
                 fps=12, width=340, start=0.0, duration=5.0)
print("视频转 GIF:", p.stat().st_size//1024, "KB")
# 抽一帧做静态图
cap = cv2.VideoCapture(str(p)); ok, f0 = cap.read(); cap.release()
if ok:
    Image.fromarray(cv2.cvtColor(f0, cv2.COLOR_BGR2RGB)).save(OUT/"视频转GIF_静态.png")
