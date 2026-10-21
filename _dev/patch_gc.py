import io
p = r"D:\agent\poster-studio\sticker.py"
t = io.open(p, encoding="utf-8").read()
if "def grabcut_alpha" not in t:
    add = '''

def grabcut_alpha(img: np.ndarray, iters: int = 5) -> np.ndarray:
    """
    GrabCut：用颜色模型分出前景。
    适合"物体 + 柔和渐变背景"（泛洪填充在这种背景上走不远）。
    """
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    rect = (max(1, int(w * 0.02)), max(1, int(h * 0.02)),
            int(w * 0.96), int(h * 0.96))
    try:
        cv2.grabCut(img, mask, rect, bgd, fgd, iters, cv2.GC_INIT_WITH_RECT)
    except Exception:
        return np.ones((h, w), np.float32)
    a = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1, 0).astype(np.float32)
    n, cc, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
    if n > 1:
        keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        a = (cc == keep).astype(np.float32)
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)).astype(np.float32)
    return cv2.GaussianBlur(a, (5, 5), 0)
'''
    t = t.replace("def robust_alpha", add + "\n\ndef robust_alpha", 1)

# 把 grabcut 加入 robust_alpha 的候选链
old_tail = """    a2 = light_bg_alpha(img)
    if good(a2):
        return a2
    return best if best is not None else a2"""
new_tail = """    a2 = light_bg_alpha(img)
    if good(a2):
        return a2

    a3 = grabcut_alpha(img)
    if good(a3):
        return a3

    # 都不理想时，选覆盖率最接近 0.4 的
    cands = [c for c in (best, a2, a3) if c is not None]
    return min(cands, key=lambda m: abs(float((m > 0.5).mean()) - 0.4))"""
if old_tail in t:
    t = t.replace(old_tail, new_tail, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("patched")
