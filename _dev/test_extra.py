import sys, numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, r"D:\agent\poster-studio")
import extra, importlib
importlib.reload(extra)
from extra import rot_float_frames, sequence_frames
from sticker import flat_bg_alpha, trim, make_sticker, encode_gif, encode_webp

root = Path(r"D:\agent\poster-studio"); out = root/"meme"

# --- 1) 鸡块旋转 ---
im = Image.open(r"D:\agent\素材\鸡块.png").convert("RGB")
arr = np.asarray(im, np.uint8)
a = flat_bg_alpha(arr, tol=20)
print("鸡块主体占比 %.0f%%" % (100*(a>0.5).mean()))
sub, al = trim(arr, a)
r2, a2 = make_sticker(sub, al, size=384, border="none", border_px=0, shadow=False)
rgba = np.dstack([r2, (a2*255).astype(np.uint8)])
fr = rot_float_frames(rgba, n=24, bg=(255,255,255))
encode_gif(fr, str(out/"nugget_spin.gif"), fps=12)
encode_webp(fr, str(out/"nugget_spin.webp"), fps=12)
print("旋转 GIF ok")

# --- 2) 倒计时序列 3-2-1 ---
imgs = []
for num, col in [("3",(233,90,90)), ("2",(240,170,60)), ("1",(80,190,110))]:
    c = Image.new("RGB",(360,360),(255,255,255))
    d = ImageDraw.Draw(c)
    d.ellipse([30,30,330,330], fill=col)
    f = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 190)
    tw = d.textlength(num, font=f)
    d.text(((360-tw)/2, 60), num, font=f, fill=(255,255,255))
    imgs.append(c)
fr2 = sequence_frames(imgs, size=480, fps=10, hold=0.5, countdown=True, fade=3)
encode_gif(fr2, str(out/"countdown.gif"), fps=10)
encode_webp(fr2, str(out/"countdown.webp"), fps=10)
print("倒计时 GIF ok")

# --- 3) 视频转 GIF ---
from extra import video_to_gif, video_info
src = r"D:\agent\sequence-evolver\artifacts\focus_anime.mp4"
print("视频信息:", video_info(src))
p = video_to_gif(src, str(out/"from_video.gif"), fps=12, width=420, start=0.5, duration=3)
print("视频转 GIF ok", "%.0f KB"%(p.stat().st_size/1024))
