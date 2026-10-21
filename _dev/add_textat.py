import io
p = r"D:\agent\poster-studio\sticker.py"
t = io.open(p, encoding="utf-8").read()
if "def add_text_at" not in t:
    t += '''

def add_text_at(rgba: np.ndarray, text: str, x_pct: float = 50.0, y_pct: float = 15.0,
                color=(255, 255, 255), stroke=(16, 16, 20),
                max_width_ratio: float = 0.86) -> np.ndarray:
    """
    在画面的任意位置画文字（x/y 用百分比，0~100）。
    (x_pct, y_pct) 是文字块中心的相对位置；超出画布会自动收进来。
    """
    if not (text or "").strip():
        return rgba
    img = Image.fromarray(rgba).convert("RGBA")
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    W, H = img.size
    max_w = W * max_width_ratio

    size = int(W * 0.115)
    while size > 14:
        font = ImageFont.truetype(FONT_BOLD[0], size)
        lines, cur = [], ""
        for ch in text.strip():
            if d.textlength(cur + ch, font=font) > max_w and cur:
                lines.append(cur); cur = ch
            else:
                cur += ch
        if cur:
            lines.append(cur)
        if len(lines) <= 3:
            break
        size -= 4

    lh = int(size * 1.18)
    total = lh * len(lines)
    cx = W * x_pct / 100.0
    cy = H * y_pct / 100.0
    y0 = cy - total / 2
    y0 = min(max(y0, 4), H - total - 4)

    for ln in lines:
        tw = d.textlength(ln, font=font)
        x = min(max(cx - tw / 2, 4), W - tw - 4)
        d.text((x, y0), ln, font=font, fill=color,
               stroke_width=max(3, size // 12), stroke_fill=stroke)
        y0 += lh

    return np.array(Image.alpha_composite(img, layer).convert("RGBA"))
'''
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("sticker.py: 已加入 add_text_at")
