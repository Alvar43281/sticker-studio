"""
画面动效（Frame Effects）
========================
这些动效作用于**整张画面**，不依赖主体轮廓 —— 任何素材都能用。

  肯·伯恩斯  缓动裁切 + 推进，最像电影镜头
  波浪扭曲    正弦位移场，画面像水面
  故障        通道错位 + 随机块位移，赛博感
  光斑漂移    多个高斯光斑游走，氛围感
  万花筒      极坐标角度折叠，对称花纹旋转
"""

from __future__ import annotations

import math
from typing import List

import cv2
import numpy as np


def _ease(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def _loop_phase(i: int, n: int) -> float:
    return i / max(n, 1)


# ---------------------------------------------------------------- 肯·伯恩斯
def ken_burns(img: np.ndarray, n: int = 24, zoom: float = 1.12,
              pan_x: float = 0.06, pan_y: float = 0.03) -> List[np.ndarray]:
    """缓动推进 + 轻微平移。首尾用同一位置，方便循环。"""
    h, w = img.shape[:2]
    out = []
    for i in range(n):
        t = _loop_phase(i, n)
        # 来回缓动：0→1→0，保证首尾衔接
        e = _ease(math.sin(math.pi * t) ** 0.7) if t < 0.5 else _ease(math.sin(math.pi * t) ** 0.7)
        s = 1.0 + (zoom - 1.0) * e
        cw, ch = max(8, int(w / s)), max(8, int(h / s))
        cx = w / 2 + pan_x * w * (e - 0.5) * 2
        cy = h / 2 + pan_y * h * (e - 0.5) * 2
        x0 = int(min(max(cx - cw / 2, 0), w - cw))
        y0 = int(min(max(cy - ch / 2, 0), h - ch))
        crop = img[y0:y0 + ch, x0:x0 + cw]
        out.append(cv2.resize(crop, (w, h), interpolation=cv2.INTER_LINEAR))
    return out


# ---------------------------------------------------------------- 波浪扭曲
def wave_distort(img: np.ndarray, n: int = 24, amp: float = 10.0,
                 cycles: float = 2.0) -> List[np.ndarray]:
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    out = []
    for i in range(n):
        t = _loop_phase(i, n)
        ph = 2 * math.pi * t
        mx = xx + amp * np.sin(2 * math.pi * yy / h * cycles + ph)
        my = yy + amp * 0.5 * np.cos(2 * math.pi * xx / w * cycles + ph)
        out.append(cv2.remap(img, mx, my, cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_REFLECT))
    return out


# ---------------------------------------------------------------- 故障
def glitch(img: np.ndarray, n: int = 24, seed: int = 7,
           strength: float = 1.0) -> List[np.ndarray]:
    """通道错位 + 随机横条位移。用周期性种子，循环不突兀。"""
    h, w = img.shape[:2]
    out = []
    for i in range(n):
        t = _loop_phase(i, n)
        rng = np.random.default_rng(seed + int(t * 6))
        f = img.copy()
        sh = int((2 + 6 * strength) * (0.5 + 0.5 * math.sin(2 * math.pi * t)))
        if sh > 0:
            f[..., 0] = np.roll(f[..., 0], sh, axis=1)
            f[..., 2] = np.roll(f[..., 2], -sh, axis=1)
        for _ in range(int(2 + 3 * strength)):
            y0 = int(rng.integers(0, max(1, h - 24)))
            bh = int(rng.integers(4, 22))
            dx = int(rng.integers(-14, 15))
            f[y0:y0 + bh] = np.roll(f[y0:y0 + bh], dx, axis=1)
        out.append(f)
    return out


# ---------------------------------------------------------------- 光斑漂移
def bokeh_drift(img: np.ndarray, n: int = 24, count: int = 14,
                seed: int = 3, tint=(255, 240, 210)) -> List[np.ndarray]:
    h, w = img.shape[:2]
    rng = np.random.default_rng(seed)
    px = rng.uniform(0, w, count)
    py = rng.uniform(0, h, count)
    rad = rng.uniform(w * 0.03, w * 0.10, count)
    spd = rng.uniform(0.4, 1.4, count)
    out = []
    for i in range(n):
        t = _loop_phase(i, n)
        acc = np.zeros((h, w), np.float32)
        for k in range(count):
            # 圆周漂移，一圈即循环
            a = 2 * math.pi * t * spd[k] + k
            x = px[k] + math.cos(a) * rad[k] * 1.4
            y = py[k] + math.sin(a) * rad[k] * 1.0
            cv2.circle(acc, (int(x) % w, int(y) % h), int(rad[k]), 1.0, -1)
        acc = cv2.GaussianBlur(acc, (0, 0), max(4.0, w / 45.0))
        acc = np.clip(acc, 0, 1)
        f = np.clip(img.astype(np.float32) + acc[..., None] * np.array(tint, np.float32) * 0.55, 0, 255)
        out.append(f.astype(np.uint8))
    return out


# ---------------------------------------------------------------- 万花筒
def kaleidoscope(img: np.ndarray, n: int = 24, segments: int = 6,
                 zoom: float = 0.9) -> List[np.ndarray]:
    """把画面折叠成扇形对称，再缓慢旋转。"""
    h, w = img.shape[:2]
    cx, cy = w / 2, h / 2
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    r = np.sqrt(dx ** 2 + dy ** 2)
    theta = np.arctan2(dy, dx)
    sect = 2 * math.pi / segments

    out = []
    for i in range(n):
        t = _loop_phase(i, n)
        rot = 2 * math.pi * t / segments
        a = np.mod(theta + rot, sect)
        a = np.abs(a - sect / 2)                     # 镜像折叠
        sx = cx + r * zoom * np.cos(a)
        sy = cy + r * zoom * np.sin(a)
        out.append(cv2.remap(img, sx.astype(np.float32), sy.astype(np.float32),
                             cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT))
    return out




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


FRAME_FX = {
    "肯·伯恩斯": ken_burns,
    "波浪扭曲": wave_distort,
    "故障": glitch,
    "光斑漂移": bokeh_drift,
    "万花筒": kaleidoscope,
    "极坐标展开": polar_warp,
    "CRT": crt,
    "半调网点": halftone,
    "老电影": old_film,
}
