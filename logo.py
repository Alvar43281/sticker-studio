"""
徽记模式（Emblem Mode）
=======================
让一个图标/徽记"从虚无中聚合成形"。

与贴纸模式的共用点：都用同一套抠图拿到精确的 alpha 形状。
区别：贴纸是"整体变形/位移"，徽记是"粒子汇聚 + 光效"。

三个阶段：
  0.00~0.45  光点从四周高速汇聚
  0.30~0.78  形状随汇聚进度逐渐显影（alpha 淡入）
  0.65~1.00  扫光掠过 + 能量脉冲，定型
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np

from sticker import encode_gif


def alpha_for_emblem(img: np.ndarray) -> np.ndarray:
    """
    徽记的 alpha 来源：先用分割模型试，模型不认（占比过小）就退回亮度阈值。
    暗底 + 亮线是徽记的典型形态，亮度法反而更准。
    """
    from sticker import cutout
    a = cutout(img)
    if float(a.mean()) > 0.03 and float((a > 0.5).mean()) > 0.02:
        return a

    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
    h, w = g.shape
    m = max(4, int(min(h, w) * 0.05))
    ring = np.concatenate([g[:m].ravel(), g[-m:].ravel(), g[:, :m].ravel(), g[:, -m:].ravel()])
    bg = float(np.median(ring))
    a = np.clip((g - (bg + 8.0)) / 46.0, 0, 1)
    a = cv2.morphologyEx((a > 0.30).astype(np.uint8), cv2.MORPH_CLOSE,
                         np.ones((3, 3), np.uint8)).astype(np.float32)
    a = cv2.GaussianBlur(a, (5, 5), 0)
    return a


def _ease(t: np.ndarray | float):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def sample_points(alpha: np.ndarray, n: int, rng) -> Tuple[np.ndarray, np.ndarray]:
    ys, xs = np.nonzero(alpha > 0.45)
    if len(xs) == 0:
        ys, xs = np.nonzero(alpha > 0.1)
    if len(xs) == 0:
        raise ValueError("alpha 为空，无法生成")
    idx = rng.choice(len(xs), min(n, len(xs)), replace=False)
    return xs[idx].astype(np.float32), ys[idx].astype(np.float32)


def make_logo(
    rgb: np.ndarray,
    alpha: np.ndarray,
    n: int = 72,
    size: int = 512,
    bg=(8, 9, 14),
    mono: bool = False,
    tint=(120, 200, 255),
    spark: int = 4200,
    seed: int = 5,
) -> List[np.ndarray]:
    rng = np.random.default_rng(seed)
    h, w = alpha.shape
    assert (h, w) == (size, size)

    tx, ty = sample_points(alpha, spark, rng)

    # 起点：画面外圈
    ang = rng.uniform(0, 2 * np.pi, len(tx))
    rad = rng.uniform(0.55, 0.95, len(tx)) * size
    sx = np.clip(size / 2 + np.cos(ang) * rad, 0, size - 1)
    sy = np.clip(size / 2 + np.sin(ang) * rad, 0, size - 1)
    delay = rng.uniform(0.0, 0.40, len(tx))

    # 目标颜色
    tcol = rgb[ty.astype(int), tx.astype(int)].astype(np.float32)
    if mono:
        tcol = np.tile(np.array(tint, np.float32)[None], (len(tx), 1))

    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    frames: List[np.ndarray] = []

    for k in range(n):
        t = k / max(n - 1, 1)

        # 主体显影
        appear = _ease(np.clip((t - 0.30) / 0.48, 0, 1))
        shape = alpha * appear

        canvas = np.zeros((size, size, 3), np.float32)
        canvas[:] = np.array(bg, np.float32)

        # 主体
        a3 = shape[..., None]
        canvas = canvas * (1 - a3) + rgb.astype(np.float32) * a3

        # 粒子
        local = _ease(np.clip((t - delay) / 0.62, 0, 1))
        px = sx + (tx - sx) * local
        py = sy + (ty - sy) * local
        xi = np.clip(px.astype(np.int32), 0, size - 1)
        yi = np.clip(py.astype(np.int32), 0, size - 1)

        acc = np.zeros((size * size, 3), np.float32)
        np.add.at(acc, xi + yi * size, tcol * (0.6 + 0.8 * (1 - local))[:, None])
        cnt = np.zeros(size * size, np.float32)
        np.add.at(cnt, xi + yi * size, 1.0)
        acc = acc.reshape(size, size, 3) / np.maximum(cnt.reshape(size, size), 1)[..., None]

        dots = (cnt.reshape(size, size) > 0).astype(np.float32)
        dots = cv2.GaussianBlur(dots, (0, 0), 0.8)
        glow = cv2.GaussianBlur(dots, (0, 0), size / 55.0) * 1.8

        canvas = canvas + acc * dots[..., None] * 1.5
        canvas = canvas + glow[..., None] * np.array(tint, np.float32) * 0.85

        # 轮廓辉光（随显现增强）
        if appear > 0.05:
            ring = np.clip(cv2.GaussianBlur(alpha, (0, 0), size / 60.0) - alpha, 0, 1)
            pulse = 0.5 + 0.5 * np.sin(t * np.pi * 3)
            canvas = canvas + (ring * appear * (0.5 + 0.5 * pulse))[..., None] * \
                     np.array(tint, np.float32) * 1.2

        # 扫光
        if t > 0.62:
            st = (t - 0.62) / 0.38
            pos = -0.25 + 1.5 * st
            band = np.exp(-((xx / size - pos) / 0.06) ** 2) * alpha
            band = cv2.GaussianBlur(band, (0, 0), size / 90.0)
            canvas = canvas + band[..., None] * np.array([255, 255, 255], np.float32) * 1.1

        # 暗角
        r = np.sqrt(((xx - size / 2) / (size / 2)) ** 2 + ((yy - size / 2) / (size / 2)) ** 2)
        canvas = canvas * np.clip(1.05 - 0.22 * r ** 2, 0, 1)[..., None]

        frames.append(np.clip(canvas, 0, 255).astype(np.uint8))

    return frames


def save_gif(frames: List[np.ndarray], out_path: str, fps: int = 20) -> Path:
    return encode_gif(frames, out_path, fps=fps)
