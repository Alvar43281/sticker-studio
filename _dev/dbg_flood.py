import numpy as np, cv2
img = np.full((60,80,3), 210, np.uint8)
img[20:40, 25:55] = (230, 180, 40)
h, w = img.shape[:2]
ff = img.copy()
mask = np.zeros((h+2, w+2), np.uint8)
fill = (255,0,255)
flags = 4 | cv2.FLOODFILL_FIXED_RANGE
for seed in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]:
    cv2.floodFill(ff, mask, seed, fill, (20,20,20), (20,20,20), flags)
bg = np.all(ff == np.array([255,0,255], np.uint8), axis=2)
print("bg 占比 %.0f%%" % (100*bg.mean()))
print("覆盖（主体）占比 %.0f%%" % (100*(~bg).mean()))
