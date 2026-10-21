from pathlib import Path
from PIL import Image
out = Path(r"D:\agent\poster-studio\meme")
# 正确做法：alpha 合成到白底，而不是直接丢弃 alpha
for k in ["kangaroo","nailong_happy","nailong_sleep","laugh","hajimi"]:
    for pre in ("static","plain"):
        p = out/f"{pre}_{k}.png"
        if not p.exists(): continue
        rgba = Image.open(p).convert("RGBA")
        bg = Image.new("RGBA", rgba.size, (255,255,255,255))
        Image.alpha_composite(bg, rgba).convert("RGB").save(out/f"{pre}_{k}_w.png")
print("预览重做完成")

W=210
sheet = Image.new("RGB",(W*4, W*2),(245,245,248))
for i,k in enumerate(["kangaroo","nailong_happy","nailong_sleep","laugh"]):
    sheet.paste(Image.open(out/f"static_{k}_w.png").resize((W,W)), (i*W,0))
    sheet.paste(Image.open(out/f"plain_{k}_w.png").resize((W,W)), (i*W,W))
sheet.save(out/"border_compare.png")
print("对比图 ok")
