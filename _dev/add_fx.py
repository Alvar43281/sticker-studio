import io
p = r"D:\agent\poster-studio\fx.py"
t = io.open(p, encoding="utf-8").read()

add = '''

# ---------------------------------------------------------------- 极坐标
def polar_warp(img: np.ndarray, n: int = 24, rotate: float = 1.0,
               radius: float = 0.92) -> List[np.ndarray]:
    """
    极坐标展开：把画面卷成一个环，并缓慢旋转。
    输出按「角度→横轴、半径→纵轴」取样，所以圆心被拉成边缘。
    """
    h, w = img.shape[:2]
    cx, cy = w / 2, h / 2
    R = min(cx, cy) * radius
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    theta = xx / w * 2 * math.pi
    r = yy / h * R

    out = []
    for i in range(n):
        t = i / max(n, 1)
        th = theta + 2 * math.pi * t * rotate
        sx = cx + r * np.cos(th)
        sy = cy + r * np.sin(th)
        out.append(cv2.remap(img, sx.astype(np.float32), sy.astype(np.float32),
                             cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT))
    return out


# ---------------------------------------------------------------- CRT
def crt(img: np.ndarray, n: int = 24, line_gap: int = 3,
        strength: float = 1.0) -> List[np.ndarray]:
    """老电视：扫描线 + 滚动亮带 + 轻微色差 + 暗角。"""
    h, w = img.shape[:2]
    lines = np.ones((h, 1), np.float32)
    lines[::line_gap] = 1.0 - 0.35 * strength
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vig = np.clip(1.05 - 0.30 * (((xx - w / 2) / (w / 2)) ** 2 +
                                 ((yy - h / 2) / (h / 2)) ** 2), 0, 1)

    out = []
    for i in range(n):
        t = i / max(n, 1)
        f = img.astype(np.float32)
        # 色差
        f[..., 0] = np.roll(f[..., 0], 1, axis=1)
        f[..., 2] = np.roll(f[..., 2], -1, axis=1)
        # 扫描线
        f = f * lines
        # 滚动亮带
        band_y = (t * h * 2) % h
        band = np.exp(-((yy - band_y) / (h * 0.06)) ** 2) * 0.22
        f = f + band[..., None] * 255
        # 暗角 + 轻微闪烁
        f = f * vig[..., None] * (0.97 + 0.03 * math.sin(2 * math.pi * t * 6))
        out.append(np.clip(f, 0, 255).astype(np.uint8))
    return out


# ---------------------------------------------------------------- 半调网点
def halftone(img: np.ndarray, n: int = 24, cell: int = 7,
             pulse: float = 0.25) -> List[np.ndarray]:
    """半调网点：按亮度画大小不同的圆点，点径随节拍呼吸。"""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    gx, gy = w // cell + 1, h // cell + 1
    small = cv2.resize(gray, (gx, gy), interpolation=cv2.INTER_AREA)

    out = []
    for i in range(n):
        t = i / max(n, 1)
        k = 1.0 + pulse * math.sin(2 * math.pi * t)
        canvas = np.full((h, w), 255, np.float32)
        for y in range(gy):
            for x in range(gx):
                v = small[y, x]
                rad = (1 - v) * cell * 0.62 * k
                if rad < 0.6:
                    continue
                cv2.circle(canvas, (x * cell + cell // 2, y * cell + cell // 2),
                           int(rad), float(v * 255), -1)
        out.append(cv2.cvtColor(np.clip(canvas, 0, 255).astype(np.uint8),
                                cv2.COLOR_GRAY2RGB))
    return out


# ---------------------------------------------------------------- 老电影
def old_film(img: np.ndarray, n: int = 24, seed: int = 11) -> List[np.ndarray]:
    """颗粒 + 划痕 + 闪烁 + 棕褐色调。"""
    h, w = img.shape[:2]
    base = img.astype(np.float32)
    sepia = np.array([[0.393, 0.769, 0.189],
                      [0.349, 0.686, 0.168],
                      [0.272, 0.534, 0.131]], np.float32)
    base = np.clip(base @ sepia.T, 0, 255)

    out = []
    for i in range(n):
        t = i / max(n, 1)
        rng = np.random.default_rng(seed + int(t * 8))
        f = base.copy()
        noise = rng.normal(0, 9, (h, w, 1)).astype(np.float32)
        f = f + noise
        for _ in range(int(rng.integers(1, 4))):
            x = int(rng.integers(0, w))
            cv2.line(f, (x, 0), (x + int(rng.integers(-4, 5)), h), (235, 225, 200), 1)
        f = f * (0.92 + 0.08 * math.sin(2 * math.pi * t * 8))
        out.append(np.clip(f, 0, 255).astype(np.uint8))
    return out
'''
t = t.replace('FRAME_FX = {', add + '\n\nFRAME_FX = {')
t = t.replace('''FRAME_FX = {
    "肯·伯恩斯": ken_burns,
    "波浪扭曲": wave_distort,
    "故障": glitch,
    "光斑漂移": bokeh_drift,
    "万花筒": kaleidoscope,
}''', '''FRAME_FX = {
    "肯·伯恩斯": ken_burns,
    "波浪扭曲": wave_distort,
    "故障": glitch,
    "光斑漂移": bokeh_drift,
    "万花筒": kaleidoscope,
    "极坐标展开": polar_warp,
    "CRT": crt,
    "半调网点": halftone,
    "老电影": old_film,
}''')
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("fx.py 扩展完成")
