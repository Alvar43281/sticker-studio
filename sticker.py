"""
表情包工坊
==========
上传照片 → 自动抠图 → 贴纸化 → 配文 → 动效 → 导出 GIF/MP4

三段能力：
  1. 抠图：anime-seg（ONNX）出 alpha，再做边缘羽化、去杂点
  2. 贴纸化：白边/黑边/投影，画布留白
  3. 动效：程序化运动（抖动/弹跳/冲击/摇摆/呼吸）+ 文字弹出
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def _find_ffmpeg() -> str:
    env = os.environ.get("FFMPEG_PATH")
    if env and Path(env).exists():
        return env
    for cand in (r"D:\agent\tools\ffmpeg\bin\ffmpeg.exe",
                 "/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        if Path(cand).exists():
            return cand
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


_FONT_DIR = Path(__file__).resolve().parent / "fonts"
_NOTO = str(_FONT_DIR / "NotoSansCJKsc-Bold.otf")


def _pick_font(cands):
    """把第一台存在的中文字体提到 [0]，下游都用 FONT_BOLD[0]。"""
    for c in cands:
        if Path(c).exists():
            return [c] + [x for x in cands if x != c]
    return list(cands)


FONT_BOLD = _pick_font([
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    _NOTO,                      # 随包携带（Linux 云主机用，开源 OFL 授权）
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
])
FONT_REG = _pick_font([
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    _NOTO,
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
])


def _resolve_seg_model() -> str:
    env = os.environ.get("SEG_MODEL_PATH")
    if env and Path(env).exists():
        return env
    here = Path(__file__).resolve().parent
    for cand in (here / "models" / "isnetis.onnx",
                 here.parent / "models" / "isnetis.onnx",
                 Path(r"D:\agent\sequence-evolver\models\isnetis.onnx")):
        if cand.exists():
            return str(cand)
    return str(here / "models" / "isnetis.onnx")


FFMPEG = _find_ffmpeg()
SEG_MODEL = _resolve_seg_model()

_seg = None


# ---------------------------------------------------------------- 抠图
def _ensure_model(path: str) -> str:
    """模型不存在时尝试从 HuggingFace 拉取（云端首次启动用）。"""
    if Path(path).exists():
        return path
    # 默认不联网拉模型：装不上模型的环境直接走传统分割，避免首屏等待
    if os.environ.get("SEG_AUTO_DOWNLOAD", "0") != "1":
        return path
    try:
        from huggingface_hub import hf_hub_download
        fp = hf_hub_download("skytnt/anime-seg", "isnetis.onnx")
        return fp
    except Exception:
        return path


def _session():
    global _seg
    if _seg is None:
        import onnxruntime as ort
        try:
            path = _ensure_model(SEG_MODEL)
            if not Path(path).exists():
                _seg = False
            else:
                _seg = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
        except Exception:
            _seg = False
    return _seg or None


def cutout(img: np.ndarray) -> np.ndarray:
    """返回 0~1 的 alpha。模型不可用时自动退回传统分割，保证任何环境都能直接跑。"""
    sess = _session()
    if sess is None:
        return robust_alpha(img)
    h, w = img.shape[:2]
    x = cv2.resize(img, (1024, 1024), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
    x = (x - 0.5) / 0.5
    x = x.transpose(2, 0, 1)[None]
    out = sess.run(None, {sess.get_inputs()[0].name: x})[0][0][0]
    a = np.clip(out, 0, 1)
    a = cv2.resize(a, (w, h), interpolation=cv2.INTER_LINEAR)

    # 去小连通域，避免零碎噪点
    b = (a > 0.45).astype(np.uint8)
    n, cc, st, _ = cv2.connectedComponentsWithStats(b, 8)
    if n > 1:
        keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        b = (cc == keep).astype(np.uint8)
    a = np.maximum(a, cv2.GaussianBlur(b.astype(np.float32), (7, 7), 0) * 0.9)

    # 边缘修剪：把低置信度的半透明"光晕"压掉，但保留主体
    a = np.clip((a - 0.18) / 0.55, 0, 1)

    a = cv2.GaussianBlur(a, (5, 5), 0)
    return a


def trim(img: np.ndarray, alpha: np.ndarray, pad_ratio: float = 0.06) -> Tuple[np.ndarray, np.ndarray]:
    """按 alpha 裁到主体，四周留白。"""
    ys, xs = np.nonzero(alpha > 0.3)
    if len(xs) == 0:
        return img, alpha
    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()
    pad = int(max(x1 - x0, y1 - y0) * pad_ratio)
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(img.shape[1], x1 + pad), min(img.shape[0], y1 + pad)
    return img[y0:y1, x0:x1], alpha[y0:y1, x0:x1]


# ---------------------------------------------------------------- 贴纸
def make_sticker(img: np.ndarray, alpha: np.ndarray, size: int = 512,
                 border: str = "white", border_px: int = 10,
                 shadow: bool = True, pixel: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    """把抠好的主体做成贴纸：加描边、投影，居中放进方形画布。"""
    h, w = alpha.shape
    scale = (size * 0.78) / max(h, w)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    img = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA)
    alpha = cv2.resize(alpha, (nw, nh), interpolation=cv2.INTER_AREA)

    if pixel:
        small = cv2.resize(img, (max(8, nw // 10), max(8, nh // 10)), interpolation=cv2.INTER_AREA)
        img = cv2.resize(small, (nw, nh), interpolation=cv2.INTER_NEAREST)
        alpha = cv2.resize(cv2.resize(alpha, (max(8, nw // 10), max(8, nh // 10)),
                                      interpolation=cv2.INTER_AREA), (nw, nh), interpolation=cv2.INTER_NEAREST)

    # 描边：alpha 膨胀 - 原 alpha
    if border_px > 0 and border != "none":
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (border_px * 2 + 1, border_px * 2 + 1))
        dil = cv2.dilate((alpha > 0.3).astype(np.uint8), k).astype(np.float32)
        outline = np.clip(dil - alpha, 0, 1)
        outline = cv2.GaussianBlur(outline, (3, 3), 0)
    else:
        outline = np.zeros_like(alpha)

    canvas = np.zeros((size, size, 4), np.float32)
    oy, ox = (size - nh) // 2, (size - nw) // 2

    # 投影（更柔和，偏移更小）
    if shadow:
        sh = np.zeros((size, size), np.float32)
        sh[oy + 6:oy + 6 + nh, ox + 4:ox + 4 + nw] = alpha
        sh = cv2.GaussianBlur(sh, (0, 0), max(6.0, size / 60.0)) * 0.38
        canvas[..., 3] = np.maximum(canvas[..., 3], sh)

    # 描边层
    if outline.max() > 0:
        oc = np.zeros((size, size), np.float32)
        oc[oy:oy + nh, ox:ox + nw] = outline
        col = {"white": (255, 255, 255), "black": (20, 20, 24),
               "gold": (240, 196, 92)}.get(border, (255, 255, 255))
        oa = oc[..., None]
        canvas[..., :3] = canvas[..., :3] * (1 - oa) + np.array(col, np.float32) * oa
        canvas[..., 3] = np.maximum(canvas[..., 3], oc)

    # 内描边：主体边界压一条 2px 深色线，白边在白底上也能分辨
    er = cv2.erode((alpha > 0.5).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32)
    edge = np.clip((alpha > 0.5).astype(np.float32) - er, 0, 1) * 0.55
    if edge.max() > 0:
        ec = np.zeros((size, size), np.float32)
        ec[oy:oy + nh, ox:ox + nw] = edge
        ea = ec[..., None] * 0.6

    # 主体层（先压内描边，再合成）
    sub = np.zeros((size, size, 4), np.float32)
    sub[oy:oy + nh, ox:ox + nw, :3] = img
    sub[oy:oy + nh, ox:ox + nw, 3] = alpha
    if edge.max() > 0:
        sub[..., :3] = sub[..., :3] * (1 - ea) + np.array([38, 38, 48], np.float32) * ea
    a = sub[..., 3:4]
    canvas[..., :3] = sub[..., :3] * a + canvas[..., :3] * (1 - a)
    canvas[..., 3] = np.maximum(canvas[..., 3], sub[..., 3])

    return canvas[..., :3].astype(np.uint8), np.clip(canvas[..., 3], 0, 1)


# ---------------------------------------------------------------- 配文
def add_text(rgba: np.ndarray, top: str, bottom: str,
             color=(255, 255, 255), stroke=(16, 16, 20)) -> np.ndarray:
    img = Image.fromarray(rgba).convert("RGBA")
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    W, H = img.size

    def draw_lines(text: str, anchor_top: bool):
        if not text.strip():
            return
        size = int(W * 0.115)
        while size > 16:
            font = ImageFont.truetype(FONT_BOLD[0], size)
            lines, cur = [], ""
            for ch in text:
                if d.textlength(cur + ch, font=font) > W * 0.88 and cur:
                    lines.append(cur)
                    cur = ch
                else:
                    cur += ch
            if cur:
                lines.append(cur)
            if len(lines) <= 2:
                break
            size -= 4
        lh = int(size * 1.18)
        total = lh * len(lines)
        y = int(H * 0.045) if anchor_top else H - int(H * 0.045) - total
        for ln in lines:
            tw = d.textlength(ln, font=font)
            x = (W - tw) / 2
            d.text((x, y), ln, font=font, fill=color,
                   stroke_width=max(3, size // 12), stroke_fill=stroke)
            y += lh

    draw_lines(top, True)
    draw_lines(bottom, False)
    return np.array(Image.alpha_composite(img, layer).convert("RGBA"))


# ---------------------------------------------------------------- 动效
def _ease_out_back(t: float) -> float:
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def motion(preset: str, t: float) -> dict:
    """返回该帧的 (dx, dy, scale, rot)。t ∈ [0,1]。"""
    import math
    if preset == "抖动":
        amp = 7.0
        w = 2 * math.pi
        return dict(dx=amp * math.sin(t * w * 3), dy=amp * math.cos(t * w * 3),
                    scale=1.0, rot=1.2 * math.sin(t * w * 3))
    if preset == "弹跳":
        yy = abs(math.sin(t * math.pi * 2)) * 24
        sq = 1 + 0.05 * math.cos(t * math.pi * 4)
        return dict(dx=0, dy=-yy, scale=1 / sq, rot=0)
    if preset == "冲击":
        s = 0.82 + 0.18 * _ease_out_back(min(1.0, t * 3))
        return dict(dx=0, dy=0, scale=s, rot=0)
    if preset == "摇摆":
        return dict(dx=0, dy=0, scale=1.0, rot=6 * math.sin(t * 2 * math.pi))
    if preset == "呼吸":
        return dict(dx=0, dy=0, scale=1 + 0.04 * math.sin(t * 2 * math.pi), rot=0)
    if preset == "果冻":
        return dict(dx=0, dy=0, scale=1 + 0.03 * math.sin(t * math.pi * 2), rot=0)
    if preset == "流光":
        return dict(dx=0, dy=0, scale=1 + 0.02 * math.sin(t * math.pi * 2), rot=0)
    if preset == "残影":
        s = 1.0 + 0.10 * math.sin(t * math.pi * 2) ** 2
        return dict(dx=0, dy=0, scale=s, rot=0)
    if preset == "崩解":
        return dict(dx=0, dy=0, scale=1.0, rot=0)
    return dict(dx=0, dy=0, scale=1.0, rot=0)



def _apply(rgba: np.ndarray, dx: float, dy: float, scale: float, rot: float) -> np.ndarray:
    h, w = rgba.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale)
    M[0, 2] += dx
    M[1, 2] += dy
    return cv2.warpAffine(rgba, M, (w, h), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
def _jelly(rgba: np.ndarray, t: float) -> np.ndarray:
    """果冻形变：按纵向正弦做横向位移，幅度随离地高度衰减。"""
    h, w = rgba.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    amp = 10.0 * np.sin(t * np.pi * 4) * np.exp(-t * 1.2)
    falloff = (yy / h) ** 1.6            # 顶部晃动小、底部晃动大
    mx = xx + amp * falloff * np.sin(yy / (h * 0.12) + t * 9.0)
    my = yy + amp * 0.35 * falloff * np.cos(xx / (w * 0.16) + t * 7.0)
    return cv2.remap(rgba, mx.astype(np.float32), my.astype(np.float32),
                     interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                     borderValue=(0, 0, 0, 0))


def _add_glow(frame: np.ndarray, alpha: np.ndarray, t: float,
              color=(150, 220, 255), sweep: bool = False) -> np.ndarray:
    """外发光 + 可选扫光。只加在轮廓外侧，且只在暗处提亮，避免冲白。"""
    h, w = alpha.shape
    pulse = 0.55 + 0.45 * np.sin(t * np.pi * 2) ** 2
    halo = np.clip(cv2.GaussianBlur(alpha, (31, 31), 0) - alpha, 0, 1) * pulse

    headroom = np.clip(1.0 - frame / 255.0, 0, 1)      # 越亮加得越少
    out = frame + halo[..., None] * np.array(color, np.float32) * 0.9 * headroom

    if sweep:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        pos = -0.3 + 1.6 * ((t * 1.4) % 1.0)
        band = np.exp(-((xx / w - pos) / 0.07) ** 2) * alpha
        band = cv2.GaussianBlur(band, (0, 0), 6)
        out = out + band[..., None] * np.array([255, 255, 255], np.float32) * 0.55 * headroom
    return out


def _burst(rgba: np.ndarray, t: float, seed: int = 3) -> np.ndarray:
    """边缘崩解：把边缘像素向外打散，再在末段聚回。"""
    h, w = rgba.shape[:2]
    alpha = rgba[..., 3].astype(np.float32) / 255.0
    edge = np.clip(alpha - cv2.erode((alpha > 0.4).astype(np.uint8),
                                     np.ones((5, 5), np.uint8)).astype(np.float32), 0, 1)
    ys, xs = np.nonzero(edge > 0.2)
    out = rgba.copy()
    if len(xs) == 0:
        return out
    rng = np.random.default_rng(seed)
    n = min(900, len(xs))
    sel = rng.choice(len(xs), n, replace=False)
    px, py = xs[sel], ys[sel]

    # 0→0.45 飞散，0.45→1 回收
    k = np.where(t < 0.45, t / 0.45, 1 - (t - 0.45) / 0.55)
    ang = rng.uniform(0, 2 * np.pi, n)
    spd = rng.uniform(25, 90, n) * k
    cx, cy = w / 2, h / 2
    dx = (px - cx); dy = (py - cy)
    norm = np.sqrt(dx ** 2 + dy ** 2) + 1e-6
    nx = np.clip((px + dx / norm * spd + np.cos(ang) * spd * 0.4).astype(int), 0, w - 1)
    ny = np.clip((py + dy / norm * spd + np.sin(ang) * spd * 0.4).astype(int), 0, h - 1)

    # 抹掉原位边缘，在目标位置补光点
    keep = (k < 0.15)
    if not keep:
        out[py, px, 3] = (out[py, px, 3].astype(np.float32) * (1 - 0.55 * (1 - k) / (1 - 0.45 + 1e-6))).astype(np.uint8)
    for i in range(n):
        cv2.circle(out, (nx[i], ny[i]), 1, (255, 245, 220, 255), -1, cv2.LINE_AA)
    return out


def render_frames(rgba: np.ndarray, preset: str, n: int = 24,
                  bg=(255, 255, 255), glow: bool = False,
                  trail: bool = False) -> List[np.ndarray]:
    frames = []
    prev = None
    alpha0 = rgba[..., 3].astype(np.float32) / 255.0
    for i in range(n):
        t = i / max(n - 1, 1)
        if preset == "果冻":
            moved = _jelly(rgba, t)
        elif preset == "崩解":
            moved = _burst(rgba, t)
        else:
            m = motion(preset, t)
            moved = _apply(rgba, m["dx"], m["dy"], m["scale"], m["rot"])

        a = moved[..., 3:4].astype(np.float32) / 255.0
        rgb = moved[..., :3].astype(np.float32)
        canvas = rgb * a + np.array(bg, np.float32) * (1 - a)

        if glow:
            canvas = _add_glow(canvas, a[..., 0], t, sweep=(preset == "流光"))

        if trail and prev is not None:
            canvas = np.maximum(canvas, prev * 0.72)
        prev = canvas.copy()

        frames.append(np.clip(canvas, 0, 255).astype(np.uint8))
    return frames


def encode_gif(frames: List[np.ndarray], out_path: str, fps: int = 15) -> Path:
    """两遍调色板，保证 GIF 不脏。"""
    import subprocess, tempfile
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        for i, f in enumerate(frames):
            cv2.imwrite(str(Path(td) / f"f{i:04d}.png"), cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
        pal = Path(td) / "pal.png"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-framerate", str(fps),
                        "-i", str(Path(td) / "f%04d.png"),
                        "-vf", "palettegen=stats_mode=diff", str(pal)], check=True)
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-framerate", str(fps),
                        "-i", str(Path(td) / "f%04d.png"), "-i", str(pal),
                        "-lavfi", "paletteuse=dither=bayer:bayer_scale=3",
                        "-loop", "0", str(out_path)], check=True)
    return out_path



def encode_webp(frames: List[np.ndarray], out_path: str, fps: int = 15,
                quality: int = 82) -> Path:
    """动图 WebP：体积通常只有 GIF 的 1/5，且支持半透明。"""
    out_path = Path(out_path)
    dur = int(1000 / max(fps, 1))
    imgs = [Image.fromarray(f).convert("RGB") for f in frames]
    imgs[0].save(out_path, save_all=True, append_images=imgs[1:],
                 duration=dur, loop=0, quality=quality, method=6)
    return out_path

def flat_bg_alpha(img: np.ndarray, tol: int = 30) -> np.ndarray:
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




def sat_alpha(img: np.ndarray, s0: float = 0.10, s1: float = 0.26) -> np.ndarray:
    """
    饱和度分离：主体有颜色、背景是中性的灰/白时最有效。
    （很多表情包都是"彩色物体 + 浅灰底"）
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
    s = hsv[..., 1] / 255.0
    a = np.clip((s - s0) / max(s1 - s0, 1e-6), 0, 1)
    a = cv2.morphologyEx((a > 0.4).astype(np.uint8), cv2.MORPH_CLOSE,
                         np.ones((9, 9), np.uint8)).astype(np.float32)
    n, cc, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
    if n > 1:
        keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        a = (cc == keep).astype(np.float32)
    return cv2.GaussianBlur(a, (5, 5), 0)


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

    a_sat = sat_alpha(img)
    if good(a_sat):
        return a_sat

    a2 = light_bg_alpha(img)
    if good(a2):
        return a2

    a3 = grabcut_alpha(img)
    if good(a3):
        return a3

    # 都不理想时，选覆盖率最接近 0.4 的
    cands = [c for c in (best, a2, a3) if c is not None]
    return min(cands, key=lambda m: abs(float((m > 0.5).mean()) - 0.4))


def auto_cutout(img: np.ndarray) -> np.ndarray:
    """
    先试分割模型，再试平背景泛洪，取更合理的那个。
    判据：主体占比落在 8%~85% 之间，且平背景版本的边缘更贴。
    """
    a_model = cutout(img)
    r_model = float((a_model > 0.5).mean())
    a_flat = flat_bg_alpha(img)
    r_flat = float((a_flat > 0.5).mean())

    def ok(r):
        return 0.08 <= r <= 0.85

    if ok(r_flat) and not ok(r_model):
        return a_flat
    if ok(r_model) and not ok(r_flat):
        return a_model
    if ok(r_model) and ok(r_flat):
        # 都可用时，选面积更接近 0.35 的（避免把背景算进来）
        return a_flat if abs(r_flat - 0.35) < abs(r_model - 0.35) else a_model
    return a_flat if r_flat > r_model else a_model

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
