"""
扩展功能
========
1. 旋转悬浮动效（麦乐鸡块那种：物体悬空自转 + 下方投影随高度变化）
2. 多图序列 GIF（按顺序逐张呈现，可叠加倒计时数字）
3. 视频转 GIF（ffmpeg 两遍调色板）
"""

from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from sticker import FFMPEG
from sticker import FONT_BOLD


# ---------------------------------------------------------------- 旋转悬浮
def rot_float_frames(rgba: np.ndarray, n: int = 24, bg=(255, 255, 255),
                     spin: float = 1.0, bob: float = 0.10,
                     shadow: bool = True, shadow_rgb=(0, 0, 0),
                     shadow_alpha: int = 90) -> List[np.ndarray]:
    """
    旋转悬浮：绕竖轴自转（用横向压扁模拟 3D），同时上下浮动。
    下方椭圆投影随高度缩小、变淡 —— 这是"悬浮感"的关键。
    """
    h, w = rgba.shape[:2]
    img = Image.fromarray(rgba, "RGBA")
    a0 = rgba[..., 3].astype(np.float32) / 255.0
    ys, xs = np.nonzero(a0 > 0.3)
    if len(xs):
        cx0, cy0 = int(xs.mean()), int(ys.mean())
        obj_w = xs.max() - xs.min()
        obj_h = ys.max() - ys.min()
    else:
        cx0, cy0, obj_w, obj_h = w // 2, h // 2, w, h

    frames = []
    for i in range(n):
        t = i / max(n - 1, 1)
        ang = t * 2 * math.pi * spin
        sx = abs(math.cos(ang))
        flip = math.cos(ang) < 0
        rise = (1 - math.cos(t * 2 * math.pi)) / 2        # 0..1 平滑起落
        dy = -bob * h * rise

        # --- 投影 ---
        canvas = Image.new("RGBA", (w, h), tuple(bg) + (255,))
        if shadow:
            sh_w = int(obj_w * (0.95 - 0.35 * rise))
            sh_h = max(6, int(obj_h * 0.10))
            sh_cx = cx0
            sh_cy = int(cy0 + obj_h * 0.55)
            sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(sh)
            alpha = int(shadow_alpha * (1 - 0.55 * rise))
            d.ellipse([sh_cx - sh_w // 2, sh_cy - sh_h // 2,
                       sh_cx + sh_w // 2, sh_cy + sh_h // 2],
                      fill=tuple(shadow_rgb) + (alpha,))
            sh = sh.filter(ImageFilter.GaussianBlur(max(2, sh_h // 2)))
            canvas = Image.alpha_composite(canvas, sh)

        # --- 物体：横向压扁 + 镜像 + 位移 ---
        new_w = max(2, int(w * sx))
        squeezed = img.resize((new_w, h), Image.BILINEAR)
        if flip:
            squeezed = squeezed.transpose(Image.FLIP_LEFT_RIGHT)
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        layer.paste(squeezed, ((w - new_w) // 2, int(dy)), squeezed)
        canvas = Image.alpha_composite(canvas, layer)
        frames.append(np.array(canvas.convert("RGB"), dtype=np.uint8))

    return frames


# ---------------------------------------------------------------- 序列 / 倒计时
def _fit_square(im: Image.Image, size: int, pad_color=(255, 255, 255)) -> Image.Image:
    im = im.convert("RGBA")
    w, h = im.size
    s = max(w, h)
    canvas = Image.new("RGBA", (s, s), tuple(pad_color) + (255,))
    canvas.paste(im, ((s - w) // 2, (s - h) // 2), im)
    return canvas.resize((size, size), Image.LANCZOS)


def _big_text(img: Image.Image, text: str, y_ratio: float = 0.78,
              color=(255, 255, 255), stroke=(0, 0, 0)) -> Image.Image:
    if not text:
        return img
    layer = img.convert("RGBA")
    d = ImageDraw.Draw(layer)
    W, H = layer.size
    size = int(W * 0.30)
    font = None
    for p in FONT_BOLD:
        if Path(p).exists():
            font = ImageFont.truetype(p, size)
            break
    if font is None:
        return img
    tw = d.textlength(text, font=font)
    x = (W - tw) / 2
    y = int(H * y_ratio) - size // 2
    d.text((x, y), text, font=font, fill=color,
           stroke_width=max(4, size // 12), stroke_fill=stroke)
    return layer


def sequence_frames(
    images: List[Image.Image],
    size: int = 480,
    fps: int = 10,
    hold: float = 0.5,
    countdown: bool = False,
    fade: int = 2,
    bg=(255, 255, 255),
) -> List[np.ndarray]:
    """
    多图序列：按顺序逐张呈现。
    countdown=True 时自动叠加 N..1 的倒计时数字。
    fade>0 时相邻图片之间做几帧交叉淡化。
    """
    seq = [_fit_square(im, size, bg) for im in images]
    n_each = max(2, int(hold * fps))
    frames: List[np.ndarray] = []

    for idx, im in enumerate(seq):
        label = str(len(seq) - idx) if countdown else ""
        base = _big_text(im, label)
        for k in range(n_each):
            frames.append(np.array(base.convert("RGB"), dtype=np.uint8))

        # 与下一张做淡化过渡
        if fade > 0 and idx < len(seq) - 1:
            nxt = _big_text(seq[idx + 1], str(len(seq) - idx - 1) if countdown else "")
            for k in range(1, fade + 1):
                t = k / (fade + 1)
                mixed = Image.blend(base.convert("RGB"), nxt.convert("RGB"), t)
                frames.append(np.array(mixed, dtype=np.uint8))

    return frames


# ---------------------------------------------------------------- 视频转 GIF
def video_to_gif(src: str, out_gif: str, fps: int = 12, width: int = 480,
                 start: float = 0.0, duration: Optional[float] = None,
                 max_seconds: float = 10.0) -> Path:
    """短时视频 → GIF。两遍调色板，避免脏色。"""
    out_gif = Path(out_gif)
    out_gif.parent.mkdir(parents=True, exist_ok=True)
    dur = min(duration or max_seconds, max_seconds)

    with tempfile.TemporaryDirectory() as td:
        pal = Path(td) / "pal.png"
        pre = ["-ss", f"{start:.2f}", "-t", f"{dur:.2f}"] if (start > 0 or duration) else ["-t", f"{dur:.2f}"]
        vf = f"fps={fps},scale={width}:-1:flags=lanczos"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", *pre, "-i", src,
                        "-vf", f"{vf},palettegen=stats_mode=diff", str(pal)], check=True)
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", *pre, "-i", src,
                        "-i", str(pal), "-lavfi", f"{vf} [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=3",
                        "-loop", "0", str(out_gif)], check=True)
    return out_gif


def video_info(src: str) -> dict:
    out = subprocess.run([FFMPEG, "-i", src], capture_output=True, text=True).stderr
    info = {}
    for line in out.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            info["duration"] = int(h) * 3600 + int(m) * 60 + float(s)
        if "Video:" in line and "x" in line:
            import re
            m = re.search(r"(\d{2,5})x(\d{2,5})", line)
            if m:
                info["w"], info["h"] = int(m.group(1)), int(m.group(2))
    return info
