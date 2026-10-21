import sys, numpy as np
from PIL import Image
sys.path.insert(0, r"D:\agent\poster-studio")
from sticker import robust_alpha, grabcut_alpha
arr = np.asarray(Image.open(r"D:\agent\素材\鸡块.png").convert("RGB"), np.uint8)
print("grabcut 覆盖率 %.0f%%" % (100*(grabcut_alpha(arr)>0.5).mean()))
print("robust 覆盖率 %.0f%%" % (100*(robust_alpha(arr)>0.5).mean()))
