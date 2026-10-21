import io, re
p = r"D:\agent\poster-studio\app.py"
t = io.open(p, encoding="utf-8").read()

# 1) 动效增加「无」
t = t.replace('EFFECTS = {\n    "旋转悬浮": None,', 'EFFECTS = {\n    "无": None,\n    "旋转悬浮": None,')

# 2) 引入 add_text_at
t = t.replace("from sticker import (add_text, encode_gif, encode_webp, make_sticker,\n                     render_frames, robust_alpha, trim)",
              "from sticker import (add_text, add_text_at, encode_gif, encode_webp, make_sticker,\n                     render_frames, robust_alpha, trim)")

# 3) do_sticker 签名：文字位置改成两个百分比
t = t.replace("def do_sticker(img, border_name, bpx, text, text_pos, effect, bg_name, no_cut,",
              "def do_sticker(img, border_name, bpx, text, tx, ty, effect, bg_name, no_cut,")
t = t.replace('''        tt = (text or "").strip()
        top = tt if text_pos in ("上方", "上下") else ""
        bottom = tt if text_pos in ("下方", "上下") else ""
        rgba = add_text(np.dstack([r2, (a2 * 255).astype(np.uint8)]), top, bottom)''',
'''        rgba = add_text_at(np.dstack([r2, (a2 * 255).astype(np.uint8)]),
                           text, float(tx), float(ty))''')
t = t.replace('''        tt = (text or "").strip()
        f_top = tt if text_pos in ("上方", "上下") else ""
        f_bot = tt if text_pos in ("下方", "上下") else ""
        rgba = framed(rgb, f_top, f_bot)''',
'''        rgba = framed_at(rgb, text, float(tx), float(ty))''')

# 4) framed 也支持任意位置
t = t.replace('''    canvas.paste(im, ((size - inner) // 2, (size - inner) // 2), mask)
    return add_text(np.array(canvas), top, bottom)''',
'''    canvas.paste(im, ((size - inner) // 2, (size - inner) // 2), mask)
    return add_text_at(np.array(canvas), text, x_pct, y_pct)''')
t = t.replace("def framed(rgb: np.ndarray, top: str, bottom: str, size: int = 512) -> np.ndarray:",
              "def framed_at(rgb: np.ndarray, text: str, x_pct: float = 50.0, y_pct: float = 12.0,\n              size: int = 512) -> np.ndarray:")

# 5) 动效为「无」时只出静态 PNG
t = t.replace('''    progress(0.7, desc="生成动效…")
    bg = (255, 255, 255) if bg_name == "白" else (18, 18, 22)''',
'''    if effect == "无":
        info = "透明 PNG（静态）"
        return str(png), [str(png)], info

    progress(0.7, desc="生成动效…")
    bg = (255, 255, 255) if bg_name == "白" else (18, 18, 22)''')

# 6) UI：文字位置 -> 两个滑块
t = t.replace('''                        text = gr.Textbox(label="文字", placeholder="请输入文字", lines=1)
                        text_pos = gr.Radio(["上方", "下方", "上下"], value="上方", label="文字位置")''',
'''                        text = gr.Textbox(label="文字", placeholder="请输入文字", lines=1)
                        with gr.Row():
                            tx = gr.Slider(0, 100, value=50, step=1, label="水平位置 %")
                            ty = gr.Slider(0, 100, value=14, step=1, label="垂直位置 %")''')

# 7) 更新 inputs
t = t.replace("inputs=[image_in, border, bpx, text, text_pos, effect, bg_name, no_cut],",
              "inputs=[image_in, border, bpx, text, tx, ty, effect, bg_name, no_cut],")

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("app.py 已改：无动效 + 自由文字位置")
