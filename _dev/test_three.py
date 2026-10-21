from gradio_client import Client, handle_file
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import tempfile

c = Client("http://127.0.0.1:7870", verbose=False)
info = c.view_api(return_format="dict")
print("端点:", list(info["named_endpoints"].keys()))

# 1) 旋转悬浮
r1 = c.predict(img=handle_file(r"D:\agent\素材\鸡块.png"), border_name="无", bpx=9,
               top="", bottom="", effect="旋转悬浮", bg_name="白", no_cut=False,
               api_name="/do_sticker")
print("旋转:", [p.split("\\")[-1] for p in r1[1]])

# 2) 序列
tmp = Path(tempfile.mkdtemp())
paths = []
for i, (num, col) in enumerate([("3",(233,90,90)),("2",(240,170,60)),("1",(80,190,110))]):
    im = Image.new("RGB",(360,360),(255,255,255)); d = ImageDraw.Draw(im)
    d.ellipse([20,20,340,340], fill=col)
    f = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 200)
    tw = d.textlength(num, font=f); d.text(((360-tw)/2, 55), num, font=f, fill=(255,255,255))
    p = tmp/f"{i}.png"; im.save(p); paths.append(p)

r2 = c.predict(files=[handle_file(str(p)) for p in paths], hold=0.5, countdown=True,
               fade=3, size=480, api_name="/do_sequence")
print("序列:", [p.split("\\")[-1] for p in r2[1]])

# 3) 视频转 GIF
r3 = c.predict(video=handle_file(r"D:\agent\sequence-evolver\artifacts\focus_anime.mp4"),
               fps=12, width=420, start=0.5, dur=3, api_name="/do_video")
print("视频:", [p.split("\\")[-1] for p in r3[1]])
