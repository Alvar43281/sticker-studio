"""
贴纸工坊 · Web 界面
===================
四个功能：
  1. 贴纸模式  —— 抠图 + 配文 + 动效（含「旋转悬浮」麦乐鸡块效果）
  2. 徽记模式  —— 粒子汇聚 + 扫光
  3. 序列模式  —— 多图按顺序播放，可叠倒计时
  4. 视频转 GIF

主输出：透明背景 PNG；另附 GIF / WebP 动图。

启动：python app.py  →  http://127.0.0.1:7870
"""

import time
from pathlib import Path

import gradio as gr
import numpy as np
from PIL import Image, ImageDraw

from extra import rot_float_frames, sequence_frames, video_to_gif
from fx import FRAME_FX
from logo import alpha_for_emblem, make_logo, save_gif
from sticker import (add_text, add_text_at, encode_gif, encode_webp, make_sticker,
                     render_frames, robust_alpha, trim)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
ASSETS = ROOT / "assets"

EFFECTS = {
    "无": None,
    "旋转悬浮": None,          # 特殊处理
    "肯·伯恩斯": None, "波浪扭曲": None, "故障": None,
    "光斑漂移": None, "万花筒": None, "极坐标展开": None,
    "CRT": None, "半调网点": None, "老电影": None,
    "冲击": dict(glow=False, trail=False),
    "弹跳": dict(glow=False, trail=False),
    "抖动": dict(glow=False, trail=False),
    "摇摆": dict(glow=False, trail=False),
    "呼吸": dict(glow=False, trail=False),
    "果冻": dict(glow=False, trail=False),
    "流光": dict(glow=True, trail=False),
    "残影": dict(glow=False, trail=True),
    "崩解": dict(glow=True, trail=False),
}
BORDERS = {"无": "none", "白色": "white", "黑色": "black", "金色": "gold"}


def framed_at(rgb: np.ndarray, text: str, x_pct: float = 50.0, y_pct: float = 12.0,
              size: int = 512) -> np.ndarray:
    """不抠图：整图裁圆角 + 白框。"""
    h, w = rgb.shape[:2]
    s = min(h, w)
    sq = rgb[(h - s) // 2:(h - s) // 2 + s, (w - s) // 2:(w - s) // 2 + s]
    inner = int(size * 0.78)
    im = Image.fromarray(sq).resize((inner, inner), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    pad, rad = 10, 26
    d.rounded_rectangle([(size - inner) // 2 - pad, (size - inner) // 2 - pad,
                         (size + inner) // 2 + pad, (size + inner) // 2 + pad],
                        radius=rad, fill=(255, 255, 255, 255))
    mask = Image.new("L", (inner, inner), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, inner, inner], radius=18, fill=255)
    canvas.paste(im, ((size - inner) // 2, (size - inner) // 2), mask)
    return add_text_at(np.array(canvas), text, x_pct, y_pct)


def do_cutout(img, make_white, make_black, progress=gr.Progress()):
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


def do_sticker(img, border_name, bpx, text, tx, ty, effect, bg_name, no_cut,
               progress=gr.Progress()):
    if img is None:
        raise gr.Error("请先上传图片")
    arr = np.asarray(img.convert("RGBA"), dtype=np.uint8)
    rgb, alpha = arr[..., :3], arr[..., 3].astype(np.float32) / 255.0

    progress(0.1, desc="抠图…")
    if no_cut:
        rgba = framed_at(rgb, text, float(tx), float(ty))
    else:
        a = alpha if alpha.min() <= 0.98 else robust_alpha(rgb)
        if float((a > 0.4).mean()) < 0.02:
            raise gr.Error("没抠出主体，可勾选「不抠图」")
        sub, al = trim(rgb, a)
        r2, a2 = make_sticker(sub, al, size=512, border=BORDERS.get(border_name, "none"),
                              border_px=int(bpx))
        rgba = add_text_at(np.dstack([r2, (a2 * 255).astype(np.uint8)]),
                           text, float(tx), float(ty))

    stamp = int(time.time() * 1000)
    png = OUT / f"sticker_{stamp}.png"
    Image.fromarray(rgba, "RGBA").save(png)

    if effect == "无":
        return str(png), [str(png)], "透明 PNG（静态，无动效）"

    progress(0.65, desc="动效…")
    bg = (255, 255, 255) if bg_name == "白" else (18, 18, 22)
    if effect == "旋转悬浮":
        frames = rot_float_frames(rgba, n=24, bg=bg)
    elif effect in FRAME_FX:
        a4 = rgba[..., 3:4].astype(np.float32) / 255.0
        base = (rgba[..., :3].astype(np.float32) * a4
                + np.array(bg, np.float32) * (1 - a4)).astype(np.uint8)
        frames = FRAME_FX[effect](base, n=24)
    else:
        frames = render_frames(rgba, effect, n=20, bg=bg, **EFFECTS.get(effect, {}))

    gif = encode_gif(frames, str(OUT / f"sticker_{stamp}.gif"), fps=12)
    webp = encode_webp(frames, str(OUT / f"sticker_{stamp}.webp"), fps=12)
    info = (f"透明 PNG + 动图　|　{effect}　|　"
            f"GIF {gif.stat().st_size/1024:.0f}KB ｜ WebP {webp.stat().st_size/1024:.0f}KB")
    return str(png), [str(png), str(gif), str(webp)], info


def do_emblem(img, mono, dur, progress=gr.Progress()):
    if img is None:
        raise gr.Error("请先上传图片")
    rgb = np.asarray(img.convert("RGB"), dtype=np.uint8)
    progress(0.2, desc="提取形状…")
    a = alpha_for_emblem(rgb)
    if float((a > 0.4).mean()) < 0.003:
        raise gr.Error("没找到图形轮廓，试试暗底亮线图标")
    sub, al = trim(rgb, a, pad_ratio=0.02)
    r2, a2 = make_sticker(sub, al, size=512, border="none", border_px=0, shadow=False)

    stamp = int(time.time() * 1000)
    png = OUT / f"emblem_{stamp}.png"
    Image.fromarray(np.dstack([r2, (a2 * 255).astype(np.uint8)]), "RGBA").save(png)

    progress(0.5, desc="粒子汇聚…")
    n = max(40, int(dur * 20))
    frames = make_logo(r2, a2, n=n, size=512, mono=bool(mono), tint=(150, 205, 255))
    gif = save_gif(frames, str(OUT / f"emblem_{stamp}.gif"), fps=20)
    webp = encode_webp(frames, str(OUT / f"emblem_{stamp}.webp"), fps=20)
    return str(png), [str(png), str(gif), str(webp)], \
        f"透明 PNG + 动图　|　粒子汇聚　|　GIF {gif.stat().st_size/1024:.0f}KB"


def do_sequence(files, hold, countdown, fade, size, progress=gr.Progress()):
    if not files:
        raise gr.Error("请至少上传两张图")
    progress(0.15, desc="载入序列…")
    imgs = []
    for f in files:
        p = f if isinstance(f, str) else getattr(f, "name", str(f))
        imgs.append(Image.open(p).convert("RGB"))
    progress(0.5, desc="合成序列…")
    frames = sequence_frames(imgs, size=int(size), fps=10, hold=float(hold),
                             countdown=bool(countdown), fade=int(fade))
    stamp = int(time.time() * 1000)
    gif = encode_gif(frames, str(OUT / f"seq_{stamp}.gif"), fps=10)
    webp = encode_webp(frames, str(OUT / f"seq_{stamp}.webp"), fps=10)
    preview = OUT / f"seq_{stamp}.png"
    Image.fromarray(frames[0]).save(preview)
    return str(preview), [str(gif), str(webp)], \
        f"{len(imgs)} 张 · 每张 {hold}s　|　GIF {gif.stat().st_size/1024:.0f}KB"


def do_video(video, fps, width, start, dur, progress=gr.Progress()):
    if not video:
        raise gr.Error("请先上传视频")
    src = video if isinstance(video, str) else getattr(video, "name", str(video))
    progress(0.2, desc="转码中…")
    stamp = int(time.time() * 1000)
    gif = video_to_gif(src, str(OUT / f"video_{stamp}.gif"), fps=int(fps),
                       width=int(width), start=float(start), duration=float(dur))
    import cv2
    cap = cv2.VideoCapture(str(gif))
    ok, frame = cap.read()
    cap.release()
    preview = None
    if ok:
        preview = OUT / f"video_{stamp}.png"
        Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).save(preview)
    return (str(preview) if preview else None), [str(gif)], \
        f"GIF {gif.stat().st_size/1024:.0f}KB"


CSS = """
.gradio-container{max-width:1220px !important;margin:0 auto !important}
#title{text-align:center;margin:6px 0 0}
#subtitle{text-align:center;color:#8b93a3;font-size:13px;margin:0 0 14px}
#preview img{object-fit:contain !important;border-radius:12px;
  background:repeating-conic-gradient(#2a2d36 0% 25%, #1e2028 0% 50%) 50%/22px 22px}
footer{display:none !important}
"""




def _port_free(port: int) -> bool:
    import socket
    s = socket.socket()
    try:
        s.bind(("0.0.0.0", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def _select_tab(request: gr.Request):
    """URL 带 ?tab=cutout/sticker/emblem/sequence/video 时，自动切到对应功能。"""
    want = "cutout"
    try:
        want = (request.query_params.get("tab") or "cutout").lower()
    except Exception:
        pass
    valid = {"cutout", "sticker", "emblem", "sequence", "video"}
    return gr.update(selected=(want if want in valid else "cutout"))


def build_ui():
    with gr.Blocks(title="贴纸工坊", css=CSS) as demo:
        gr.Markdown("# 贴纸工坊", elem_id="title")
        gr.Markdown("抠图 · 贴纸 · 动效 · 序列 · 视频转 GIF", elem_id="subtitle")

        with gr.Row(equal_height=False):
            with gr.Column(scale=4, min_width=350):
                with gr.Tabs(selected="cutout") as tabs:
                    with gr.Tab("抠图", id="cutout"):
                        cut_in = gr.Image(label="上传图片", type="pil", height=230)
                        with gr.Row():
                            make_white = gr.Checkbox(value=True, label="同时导出白底图")
                            make_black = gr.Checkbox(value=False, label="同时导出深色底")
                        btn_c = gr.Button("抠图并导出", variant="primary")
                        gr.Markdown("*输出透明 PNG，可直接拖进 PPT / 微信 / 设计软件。*")

                    with gr.Tab("贴纸", id="sticker"):
                        image_in = gr.Image(label="上传图片", type="pil", height=230)
                        with gr.Row():
                            border = gr.Dropdown(list(BORDERS), value="无", label="描边")
                            effect = gr.Dropdown(list(EFFECTS), value="旋转悬浮", label="动效")
                        text = gr.Textbox(label="文字", placeholder="请输入文字", lines=1)
                        with gr.Row():
                            tx = gr.Slider(0, 100, value=50, step=1, label="水平位置 %")
                            ty = gr.Slider(0, 100, value=14, step=1, label="垂直位置 %")
                        with gr.Accordion("更多", open=False):
                            bpx = gr.Slider(4, 20, value=9, step=1, label="描边粗细")
                            bg_name = gr.Radio(["白", "黑"], value="白", label="动图底色")
                            no_cut = gr.Checkbox(value=False, label="不抠图（整图白框）")
                        btn_s = gr.Button("生成贴纸", variant="primary")

                    with gr.Tab("徽记", id="emblem"):
                        emblem_in = gr.Image(label="上传图标", type="pil", height=230)
                        with gr.Accordion("参数", open=False):
                            mono = gr.Checkbox(value=False, label="单色发光")
                            dur = gr.Slider(2, 6, value=3.6, step=0.2, label="时长（秒）")
                        btn_e = gr.Button("生成徽记", variant="primary")

                    with gr.Tab("序列", id="sequence"):
                        seq_in = gr.Files(label="按顺序上传多张图", file_count="multiple",
                                          file_types=["image"])
                        with gr.Row():
                            hold = gr.Slider(0.2, 2.0, value=0.5, step=0.1, label="每张停留(秒)")
                            fade = gr.Slider(0, 6, value=3, step=1, label="过渡帧数")
                        with gr.Row():
                            countdown = gr.Checkbox(value=True, label="叠加倒计时数字")
                            size_s = gr.Slider(320, 720, value=480, step=40, label="尺寸")
                        btn_q = gr.Button("合成序列", variant="primary")

                    with gr.Tab("视频转 GIF", id="video"):
                        vid = gr.Video(label="上传短视频", height=200)
                        with gr.Row():
                            vfps = gr.Slider(5, 24, value=12, step=1, label="帧率")
                            vwidth = gr.Slider(240, 720, value=420, step=20, label="宽度")
                        with gr.Row():
                            vstart = gr.Slider(0, 60, value=0, step=0.5, label="起点(秒)")
                            vdur = gr.Slider(1, 10, value=4, step=0.5, label="时长(秒)")
                        btn_v = gr.Button("转成 GIF", variant="primary")

            with gr.Column(scale=6, min_width=420):
                preview = gr.Image(show_label=False, height=380, elem_id="preview")
                info = gr.Markdown("*生成后这里显示结果*")
                files = gr.Files(label="下载", file_count="multiple")

        btn_s.click(do_sticker,
                    inputs=[image_in, border, bpx, text, tx, ty, effect, bg_name, no_cut],
                    outputs=[preview, files, info])
        btn_e.click(do_emblem, inputs=[emblem_in, mono, dur],
                    outputs=[preview, files, info])
        btn_q.click(do_sequence, inputs=[seq_in, hold, countdown, fade, size_s],
                    outputs=[preview, files, info])
        btn_v.click(do_video, inputs=[vid, vfps, vwidth, vstart, vdur],
                    outputs=[preview, files, info])
        demo.load(_select_tab, inputs=None, outputs=tabs)
    return demo


if __name__ == "__main__":
    if not _port_free(7870):
        raise SystemExit("端口 7870 已被占用 —— 先关掉旧的实例再启动。")
    app = build_ui()
    app.queue(default_concurrency_limit=1)
    app.launch(server_name="0.0.0.0", server_port=7870, show_error=True,
               theme=gr.themes.Soft())
