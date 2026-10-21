import io
p = r"D:\agent\poster-studio\extra.py"
t = io.open(p, encoding="utf-8").read()
# 投影支持自定义颜色（深色底时改成微光，否则黑投影看不见）
t = t.replace('''def rot_float_frames(rgba: np.ndarray, n: int = 24, bg=(255, 255, 255),
                     spin: float = 1.0, bob: float = 0.10,
                     shadow: bool = True) -> List[np.ndarray]:''',
'''def rot_float_frames(rgba: np.ndarray, n: int = 24, bg=(255, 255, 255),
                     spin: float = 1.0, bob: float = 0.10,
                     shadow: bool = True, shadow_rgb=(0, 0, 0),
                     shadow_alpha: int = 90) -> List[np.ndarray]:''')
t = t.replace('''            alpha = int(90 * (1 - 0.55 * rise))
            d.ellipse([sh_cx - sh_w // 2, sh_cy - sh_h // 2,
                       sh_cx + sh_w // 2, sh_cy + sh_h // 2],
                      fill=(0, 0, 0, alpha))''',
'''            alpha = int(shadow_alpha * (1 - 0.55 * rise))
            d.ellipse([sh_cx - sh_w // 2, sh_cy - sh_h // 2,
                       sh_cx + sh_w // 2, sh_cy + sh_h // 2],
                      fill=tuple(shadow_rgb) + (alpha,))''')
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("extra.py 已支持自定义投影色")
