from PIL import Image
from pathlib import Path
A = Path(r"D:\agent\poster-studio\assets")
im = Image.open(A/"nugget_spin.webp")
print("模式", im.mode, "尺寸", im.size, "帧数", getattr(im, "n_frames", 1))
im.seek(6)
f = im.convert("RGBA")
# 合成到深色网页底色上，看是否融为一体
bg = Image.new("RGBA", f.size, (11,12,16,255))
Image.alpha_composite(bg, f).convert("RGB").save(A/"nugget_on_dark.png")
print("已生成网页底色预览")
