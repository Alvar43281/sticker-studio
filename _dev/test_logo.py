import sys, numpy as np, cv2
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import cutout, trim, make_sticker
from logo import make_logo, save_gif, alpha_for_emblem

root = Path(r"D:\agent\poster-studio")
src = cv2.cvtColor(cv2.imread(r"D:\agent\sequence-evolver\demo_sigil.png"), cv2.COLOR_BGR2RGB)
a = alpha_for_emblem(src)
print("alpha mean %.2f" % a.mean())
img, al = trim(src, a, pad_ratio=0.02)
rgba, alpha = make_sticker(img, al, size=512, border="none", border_px=0, shadow=False)
a8 = (alpha*255).astype(np.uint8)
frames = make_logo(rgba, alpha, n=72, size=512, mono=False, tint=(150, 205, 255))
p = save_gif(frames, str(root/"logo_emblem.gif"), fps=20)
print("徽记 GIF", "%.0f KB"%(p.stat().st_size/1024))

sheet = Image.new("RGB",(5*200,200),(8,9,14))
for i,k in enumerate([0,12,28,44,68]):
    sheet.paste(Image.fromarray(frames[k]).resize((200,200)), (i*200,0))
sheet.save(root/"logo_sheet.png")
print("ok")

