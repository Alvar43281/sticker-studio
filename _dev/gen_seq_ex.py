from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
A = Path(r"D:\agent\poster-studio\assets")

# 序列：3-2-1 三联
S = 420
im = Image.new("RGB", (S, S), (246, 247, 250))
d = ImageDraw.Draw(im)
font = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 96)
cols = [(232, 88, 88), (240, 170, 60), (86, 190, 120)]
for i, num in enumerate(("3", "2", "1")):
    cx = S // 2
    cy = 78 + i * 132
    r = 52
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=cols[i])
    tw = d.textlength(num, font=font)
    d.text((cx - tw / 2, cy - 56), num, font=font, fill=(255, 255, 255))
im.save(A / "ex5_sequence.png")
print("3-2-1 序列图完成")
