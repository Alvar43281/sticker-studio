import io
p = r"D:\agent\poster-studio\sticker.py"
t = io.open(p, encoding="utf-8").read()

start = t.index("def flat_bg_alpha")
end = t.index("def auto_cutout")
new = '''def flat_bg_alpha(img: np.ndarray, tol: int = 30) -> np.ndarray:
    """
    平背景抠图：从四角泛洪填充，把连通的背景色区域吃掉。
    必须用 FIXED_RANGE（与种子色比较），否则背景有渐变时会一路漏光。
    """
    h, w = img.shape[:2]
    ff = img.copy()
    mask = np.zeros((h + 2, w + 2), np.uint8)
    fill = np.array([255, 0, 255], np.uint8)
    flags = 4 | cv2.FLOODFILL_FIXED_RANGE
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        cv2.floodFill(ff, mask, seed, tuple(int(x) for x in fill),
                      (tol, tol, tol), (tol, tol, tol), flags)
    bg = np.all(ff == fill, axis=2)
    a = (~bg).astype(np.float32)

    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, cc, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
    if n > 1:
        keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        a = (cc == keep).astype(np.float32)
    return cv2.GaussianBlur(a, (3, 3), 0)


def light_bg_alpha(img: np.ndarray, v_thr: float = 0.90, s_thr: float = 0.12) -> np.ndarray:
    """
    浅色/棋盘格背景：背景是低饱和的高亮区，主体通常有色或更暗。
    用于那些带"假透明"棋盘格的表情包。
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
    s = hsv[..., 1] / 255.0
    v = hsv[..., 2] / 255.0
    bg = (v > v_thr) & (s < s_thr)
    a = (~bg).astype(np.float32)
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, cc, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
    if n > 1:
        keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        a = (cc == keep).astype(np.float32)
    return cv2.GaussianBlur(a, (3, 3), 0)


def robust_alpha(img: np.ndarray) -> np.ndarray:
    """
    自动挑最靠谱的一路：
      1. 真实 alpha（若有）
      2. 平背景泛洪（多个容差试）
      3. 浅色/棋盘格背景
    判据：主体占比落在 10%~82%。
    """
    def good(a):
        r = float((a > 0.5).mean())
        return 0.10 <= r <= 0.82

    best = None
    for tol in (18, 30, 45):
        a = flat_bg_alpha(img, tol=tol)
        if good(a):
            return a
        if best is None or abs(float((a > 0.5).mean()) - 0.4) < abs(float((best > 0.5).mean()) - 0.4):
            best = a

    a2 = light_bg_alpha(img)
    if good(a2):
        return a2
    return best if best is not None else a2


'''
t = t[:start] + new + t[end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("patched, syntax OK")
