import numpy as np, cv2
from PIL import Image
arr = np.asarray(Image.open(r"D:\agent\素材\鸡块.png").convert("RGB"), np.uint8)
print(arr.shape, arr.dtype, "连续:", arr.flags['C_CONTIGUOUS'])
print("亮度范围", arr.min(), arr.max())
h,w = arr.shape[:2]
ff = np.ascontiguousarray(arr).copy()
mask = np.zeros((h+2,w+2), np.uint8)
fill=(255,0,255)
flags = 4 | cv2.FLOODFILL_FIXED_RANGE
for seed in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]:
    n,_,_,rect = cv2.floodFill(ff, mask, seed, fill, (25,25,25), (25,25,25), flags)
    print("seed",seed,"填充像素",n,"rect",rect)
bg = np.all(ff == np.array([255,0,255],np.uint8), axis=2)
print("bg %.0f%%  主体 %.0f%%" % (100*bg.mean(), 100*(~bg).mean()))
