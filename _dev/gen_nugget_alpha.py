import sys, math, numpy as np, cv2
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import trim, make_sticker

A = Path(r"D:\agent\poster-studio\assets")

# 抠鸡块
arr = np.asarray(Image.open(r"D:\agent\素材\鸡块.png").convert("RGB"), np.uint8)
gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY).astype(np.float32)
a = np.clip((205 - gray) / 55.0, 0, 1)
a = cv2.morphologyEx((a>0.45).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7,7),np.uint8)).astype(np.float32)
n, cc, st, _ = cv2.connectedComponentsWithStats((a>0.5).astype(np.uint8), 8)
if n>1:
    keep = 1+int(np.argmax(st[1:, cv2.CC_STAT_AREA])); a = (cc==keep).astype(np.float32)
a = cv2.GaussianBlur(a,(5,5),0)
sub, al = trim(arr, a)
r2, a2 = make_sticker(sub, al, size=340, border="none", border_px=0, shadow=False)
rgba = np.dstack([r2, (a2*255).astype(np.uint8)])

img = Image.fromarray(rgba, "RGBA")
h, w = img.size
al0 = rgba[...,3].astype(np.float32)/255.0
ys, xs = np.nonzero(al0>0.3)
cx0, cy0 = int(xs.mean()), int(ys.mean())
obj_w, obj_h = xs.max()-xs.min(), ys.max()-ys.min()

N = 24
frames = []
for i in range(N):
    t = i/(N-1)
    ang = t*2*math.pi
    sx = abs(math.cos(ang)); flip = math.cos(ang) < 0
    rise = (1-math.cos(t*2*math.pi))/2
    dy = -0.10*h*rise

    canvas = Image.new("RGBA", (w,h), (0,0,0,0))
    # 底部微光（透明背景上代替投影）
    sh = Image.new("RGBA", (w,h), (0,0,0,0))
    d = ImageDraw.Draw(sh)
    sh_w = int(obj_w*(0.95-0.35*rise)); sh_h = max(6, int(obj_h*0.10))
    d.ellipse([cx0-sh_w//2, cy0+obj_h*0.55-sh_h//2, cx0+sh_w//2, cy0+obj_h*0.55+sh_h//2],
              fill=(110,160,255,int(75*(1-0.55*rise))))
    sh = sh.filter(ImageFilter.GaussianBlur(max(2, sh_h//2)))
    canvas = Image.alpha_composite(canvas, sh)
    # 物体
    new_w = max(2, int(w*sx))
    sq = img.resize((new_w, h), Image.BILINEAR)
    if flip: sq = sq.transpose(Image.FLIP_LEFT_RIGHT)
    layer = Image.new("RGBA", (w,h), (0,0,0,0))
    layer.paste(sq, ((w-new_w)//2, int(dy)), sq)
    canvas = Image.alpha_composite(canvas, layer)
    frames.append(canvas)

out = A/"nugget_spin.webp"
frames[0].save(out, save_all=True, append_images=frames[1:], duration=83, loop=0,
               quality=88, method=6)
print("透明背景版本", out.stat().st_size//1024, "KB", frames[0].mode)
frames[6].save(A/"nugget_frame.png")
