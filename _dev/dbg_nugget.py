import sys, numpy as np, cv2
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import flat_bg_alpha, robust_alpha, trim, make_sticker
im = Image.open(r"D:\agent\素材\鸡块.png").convert("RGB")
arr = np.asarray(im, np.uint8)
print("尺寸", arr.shape, "四角像素", arr[0,0], arr[0,-1], arr[-1,0], arr[-1,-1])
a = flat_bg_alpha(arr, tol=20)
print("flat tol20 覆盖率 %.0f%%" % (100*(a>0.5).mean()))
for t in (8, 15, 30, 45):
    print(f"  tol={t}: %.0f%%" % (100*(flat_bg_alpha(arr, tol=t)>0.5).mean()))
b = robust_alpha(arr)
print("robust 覆盖率 %.0f%%" % (100*(b>0.5).mean()))
