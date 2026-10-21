import sys, numpy as np, cv2, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import robust_alpha, trim, make_sticker, add_text, render_frames, encode_gif, encode_webp
from logo import make_logo
from extra import rot_float_frames, sequence_frames, video_to_gif

A = Path(r"D:\agent\poster-studio\assets")
MAT = Path(r"D:\agent\素材")
S = 420

# 统一准备：奶龙抠图
src = np.asarray(Image.open(MAT/"奶龙_开心.png").convert("RGB"), np.uint8)
a = robust_alpha(src); sub, al = trim(src, a)
rgb, alpha = make_sticker(sub, al, size=S, border="none", border_px=0, shadow=False)
rgba = np.dstack([rgb, (alpha*255).astype(np.uint8)])
print("奶龙主体占比 %.0f%%" % (100*float((a>0.5).mean())))

def checker(size, cell=18):
    im = Image.new("RGB",(size,size),(255,255,255)); d = ImageDraw.Draw(im)
    for y in range(0,size,cell):
        for x in range(0,size,cell):
            if (x//cell+y//cell)%2: d.rectangle([x,y,x+cell-1,y+cell-1], fill=(224,227,232))
    return im

# 01 抠图：棋盘格
Image.alpha_composite(checker(S).convert("RGBA"), Image.fromarray(rgba,"RGBA")).convert("RGB").save(A/"ex5_cutout.png")

# 02 贴纸：白边 + 文字
r2, a2 = make_sticker(sub, al, size=S, border="white", border_px=9)
st = add_text(np.dstack([r2,(a2*255).astype(np.uint8)]), "奶龙", "我来啦")
bg = Image.new("RGBA",(S,S),(255,255,255,255))
Image.alpha_composite(bg, Image.fromarray(st,"RGBA")).convert("RGB").save(A/"ex5_sticker.png")

# 03 徽记：粒子汇聚（取中后段一帧 + 动图）
fr = make_logo(rgb, alpha, n=48, size=S, mono=True, tint=(150,205,255))
Image.fromarray(fr[38]).save(A/"ex5_emblem.png")
encode_webp(fr, str(A/"ex5_emblem.webp"), fps=20)

# 04 序列：3→2→1 倒计时（奶龙作背景）
seq = []
for num in ("3","2","1"):
    im = Image.fromarray(rgba, "RGBA").copy()
    bgw = Image.new("RGBA",(S,S),(255,255,255,255))
    f = Image.alpha_composite(bgw, im).convert("RGB")
    d = ImageDraw.Draw(f)
    font = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 190)
    tw = d.textlength(num, font=font)
    d.text(((S-tw)/2, 20), num, font=font, fill=(70,110,220), stroke_width=6, stroke_fill=(255,255,255))
    seq.append(f)
Image.fromarray(np.asarray(seq[0], np.uint8)).save(A/"ex5_sequence.png")
frames = sequence_frames(seq, size=360, fps=10, hold=0.5, countdown=False, fade=3)
encode_webp(frames, str(A/"ex5_sequence.webp"), fps=10)

# 05 视频转 GIF：先把奶龙旋转存成 mp4，再转回 GIF
spin = rot_float_frames(rgba, n=24, bg=(255,255,255))
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    for i,f in enumerate(spin):
        cv2.imwrite(str(td/f"f{i:04d}.png"), cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
    mp4 = td/"spin.mp4"
    subprocess.run([r"D:\agent\tools\ffmpeg\bin\ffmpeg.exe","-y","-loglevel","error",
                    "-framerate","12","-i",str(td/"f%04d.png"),
                    "-c:v","libx264","-pix_fmt","yuv420p",str(mp4)], check=True)
    g = video_to_gif(str(mp4), str(A/"ex5_video.gif"), fps=12, width=360)
    print("视频转 GIF:", g.stat().st_size//1024, "KB")

Image.fromarray(spin[6]).save(A/"ex5_video.png")
print("五个示例素材完成")
