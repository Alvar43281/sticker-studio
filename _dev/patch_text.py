import io, re
p = r"D:\agent\poster-studio\app.py"
t = io.open(p, encoding="utf-8").read()

# 1) do_sticker 改为：单个文字 + 位置
t = t.replace("def do_sticker(img, border_name, bpx, top, bottom, effect, bg_name, no_cut,",
              "def do_sticker(img, border_name, bpx, text, text_pos, effect, bg_name, no_cut,")
t = t.replace('''        rgba = add_text(np.dstack([r2, (a2 * 255).astype(np.uint8)]),
                        top.strip(), bottom.strip())''',
'''        tt = (text or "").strip()
        top = tt if text_pos in ("上方", "上下") else ""
        bottom = tt if text_pos in ("下方", "上下") else ""
        rgba = add_text(np.dstack([r2, (a2 * 255).astype(np.uint8)]), top, bottom)''')
t = t.replace('        rgba = framed(rgb, top.strip(), bottom.strip())',
              '''        tt = (text or "").strip()
        f_top = tt if text_pos in ("上方", "上下") else ""
        f_bot = tt if text_pos in ("下方", "上下") else ""
        rgba = framed(rgb, f_top, f_bot)''')

# 2) 删掉模板下拉
t = t.replace('                        tmpl = gr.Dropdown(list(TEMPLATES), value="自定义", label="模板")\n', '')
# 3) 两个文字框 -> 一个文字框 + 位置选择
t = t.replace('''                        with gr.Row():
                            top = gr.Textbox(label="上方文字", placeholder="打工吧")
                            bottom = gr.Textbox(label="下方文字", placeholder="今天也是")''',
'''                        text = gr.Textbox(label="文字", placeholder="请输入文字", lines=1)
                        text_pos = gr.Radio(["上方", "下方", "上下"], value="上方", label="文字位置")''')
# 4) 删除 apply_tmpl 与其绑定
t = re.sub(r'\n        def apply_tmpl\(name\):.*?tmpl\.change\(apply_tmpl, inputs=tmpl, outputs=\[top, bottom, effect\]\)\n',
           '\n', t, flags=re.S)
# 5) 更新 inputs
t = t.replace("inputs=[image_in, border, bpx, top, bottom, effect, bg_name, no_cut],",
              "inputs=[image_in, border, bpx, text, text_pos, effect, bg_name, no_cut],")

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("app.py 已改：单文字 + 位置，模板已移除")
