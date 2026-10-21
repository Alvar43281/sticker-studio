import sys, time, numpy as np, cv2
from PIL import Image
from pathlib import Path
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import cutout, trim, make_sticker, add_text, render_frames, encode_gif

root = Path(r"D:\agent\poster-studio")
src = cv2.cvtColor(cv2.imread(r"D:\agent\sequence-evolver\tests\anime.png"), cv2.COLOR_BGR2RGB)
t0=time.time()
a = cutout(src)
print("抠图 %.1fs, alpha 均值 %.2f" % (time.time()-t0, a.mean()))
img, al = trim(src, a)

rgba, alpha = make_sticker(img, al, size=512, border="white", border_px=10)
rgba8 = np.dstack([rgba, (alpha*255).astype(np.uint8)])
rgba8 = add_text(rgba8, "打工吧", "今天也是")
Image.fromarray(rgba8).save(root/"sticker_static.png")

for name, preset in [("shake","抖动"), ("bounce","弹跳"), ("punch","冲击")]:
    frames = render_frames(rgba8, preset, n=24, bg=(255,255,255))
    p = encode_gif(frames, str(root/f"sticker_{name}.gif"), fps=15)
    print(preset, "→", p.name, "%.1fs"%(time.time()-t0), "%.0f KB"%(p.stat().st_size/1024))
# 抽一帧看效果
frames = render_frames(rgba8, "冲击", n=24, bg=(255,255,255))
cv2.imwrite(str(root/"frame_check.png"), cv2.cvtColor(frames[20], cv2.COLOR_RGB2BGR))
print("ok")

