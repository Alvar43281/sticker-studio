import io
p = r"D:\agent\poster-studio\app.py"
t = io.open(p, encoding="utf-8").read()

# ---- 1) 新增「纯抠图」处理函数 ----
fn = '''def do_cutout(img, make_white, make_black, progress=gr.Progress()):
    """只抠图：输出透明 PNG（可选白底/黑底版本）。"""
    if img is None:
        raise gr.Error("请先上传图片")
    arr = np.asarray(img.convert("RGBA"), dtype=np.uint8)
    rgb, alpha = arr[..., :3], arr[..., 3].astype(np.float32) / 255.0

    progress(0.15, desc="分析背景…")
    a = alpha if alpha.min() <= 0.98 else robust_alpha(rgb)
    if float((a > 0.4).mean()) < 0.02:
        raise gr.Error("没抠出主体，试试主体更清楚的图")
    sub, al = trim(rgb, a, pad_ratio=0.04)
    r2, a2 = make_sticker(sub, al, size=512, border="none", border_px=0, shadow=False)

    stamp = int(time.time() * 1000)
    out = [None, None, None]
    rgba = np.dstack([r2, (a2 * 255).astype(np.uint8)])

    png = OUT / f"cut_{stamp}.png"
    Image.fromarray(rgba, "RGBA").save(png)
    out[0] = str(png)

    progress(0.6, desc="导出变体…")
    if make_white:
        f = OUT / f"cut_{stamp}_white.png"
        bg = Image.new("RGBA", (512, 512), (255, 255, 255, 255))
        Image.alpha_composite(bg, Image.fromarray(rgba, "RGBA")).convert("RGB").save(f)
        out[1] = str(f)
    if make_black:
        f = OUT / f"cut_{stamp}_dark.png"
        bg = Image.new("RGBA", (512, 512), (18, 18, 22, 255))
        Image.alpha_composite(bg, Image.fromarray(rgba, "RGBA")).convert("RGB").save(f)
        out[2] = str(f)

    files = [x for x in out if x]
    info = "透明 PNG" + (" + 白底" if make_white else "") + (" + 深色底" if make_black else "")
    return str(png), files, f"{info}　|　主体占比 {float((a>0.5).mean())*100:.0f}%"


def do_sticker('''
t = t.replace("def do_sticker(", fn, 1)

# ---- 2) 新增第一个标签页 ----
tab = '''                with gr.Tabs():
                    with gr.Tab("抠图"):
                        cut_in = gr.Image(label="上传图片", type="pil", height=230)
                        with gr.Row():
                            make_white = gr.Checkbox(value=True, label="同时导出白底图")
                            make_black = gr.Checkbox(value=False, label="同时导出深色底")
                        btn_c = gr.Button("抠图并导出", variant="primary")
                        gr.Markdown("*输出透明 PNG，可直接拖进 PPT / 微信 / 设计软件。*")

                    with gr.Tab("贴纸"):'''
t = t.replace('                with gr.Tabs():\n                    with gr.Tab("贴纸"):', tab, 1)

# ---- 3) 绑定事件 ----
hook = '''        btn_c.click(do_cutout, inputs=[cut_in, make_white, make_black],
                    outputs=[preview, files, info])
        tmpl.change(apply_tmpl'''
t = t.replace("        tmpl.change(apply_tmpl", hook, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("app.py 已加入「纯抠图」模块")
