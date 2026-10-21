"""
海报生成核心
============
输入一句主题 + 风格，输出一张成品海报。

流程：
  1. 提示词工程：主题关键词 + 风格词 + 画质词 + 负面词
  2. SD 生成背景（按比例出图）
  3. 配色分析：背景亮度决定文字黑白，主色用于强调
  4. 排版：标题/副标题/信息行，字号自适应、安全边距、视觉层级
  5. 可读性：底部渐变遮罩 + 文字描边
  6. 导出：2× 分辨率
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_BOLD = [r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf"]
FONT_REG = [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]

RATIOS = {
    "3:4": (768, 1024),
    "1:1": (1024, 1024),
    "9:16": (576, 1024),
    "16:9": (1024, 576),
}

STYLES = {
    "极简": ("minimalist, clean composition, lots of negative space, subtle gradient, "
             "soft light, muted palette, high end editorial"),
    "赛博": ("cyberpunk, neon glow, dark city, volumetric light, rain reflections, "
             "high contrast, cinematic"),
    "复古": ("retro print poster, grain texture, warm faded colors, risograph, "
             "vintage typography feel, paper texture"),
    "自然": ("natural landscape, soft sunlight, mist, pastel tones, serene, "
             "photographic, shallow depth"),
    "国风": ("chinese ink painting, misty mountains, rice paper texture, "
             "elegant negative space, muted ink tones"),
    "霓虹": ("vibrant neon lights, bold gradients, glossy surfaces, futuristic, "
             "high saturation, studio lighting"),
}

NEGATIVE = ("text, words, letters, watermark, signature, logo, low quality, "
            "blurry, jpeg artifacts, deformed, frame, border")


def _font(paths: List[str], size: int) -> ImageFont.FreeTypeFont:
    for p in paths:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


@dataclass
class Theme:
    title: str            # 中文主标题（显示）
    subtitle: str = ""    # 副标题
    meta: str = ""        # 时间/地点等信息行
    keywords: str = ""    # 英文画面关键词
    style: str = "极简"
    ratio: str = "3:4"


def build_prompt(t: Theme) -> Tuple[str, str]:
    style = STYLES.get(t.style, STYLES["极简"])[0]
    kw = (t.keywords.strip() + ", ") if t.keywords.strip() else ""
    prompt = (f"{kw}{style}, poster background, no text, centered subject, "
              f"professional, 8k, highly detailed")
    return prompt, NEGATIVE


def generate_bg(engine, theme: Theme, seed: int = 42) -> Image.Image:
    """用 SD 生成背景，直接按目标比例出图（降到 8 的倍数）。"""
    w, h = RATIOS.get(theme.ratio, RATIOS["3:4"])
    # SD 的舒适区：长边控制在 768 内
    scale = 768 / max(w, h)
    gw, gh = int(w * scale) // 8 * 8, int(h * scale) // 8 * 8
    prompt, negative = build_prompt(theme)
    img = engine.pipe(
        prompt=prompt,
        negative_prompt=negative,
        width=gw, height=gh,
        num_inference_steps=26,
        guidance_scale=7.5,
        generator=engine._generator(seed),
    ).images[0]
    return img.resize((w, h), Image.LANCZOS)


def analyze_colors(img: Image.Image) -> dict:
    """背景亮度决定文字颜色；主色用于强调线。"""
    small = np.asarray(img.resize((64, 64)), dtype=np.float32) / 255.0
    lum = float((0.299 * small[..., 0] + 0.587 * small[..., 1] + 0.114 * small[..., 2]).mean())

    # 主色：饱和度最高的那批像素的平均
    mx = small.max(axis=2)
    mn = small.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / (mx + 1e-6), 0)
    flat = small.reshape(-1, 3)
    satf = sat.reshape(-1)
    idx = np.argsort(-satf)[: max(1, len(satf) // 20)]
    accent = flat[idx].mean(axis=0)

    text_light = lum < 0.52
    return {
        "lum": lum,
        "text": (245, 245, 248) if text_light else (24, 24, 28),
        "sub": (210, 212, 220) if text_light else (70, 72, 80),
        "accent": tuple(int(np.clip(c * 255, 0, 255)) for c in accent),
        "text_light": text_light,
    }


def _wrap_needed(draw, text: str, font, max_w: int) -> List[str]:
    """按宽度断行（中文按字符，英文按词）。"""
    lines, cur = [], ""
    for ch in text:
        trial = cur + ch
        w = draw.textlength(trial, font=font)
        if w > max_w and cur:
            lines.append(cur)
            cur = ch
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def _fit_font(draw, text: str, max_w: int, base_size: int, max_lines: int,
              fonts: List[str]) -> Tuple[ImageFont.FreeTypeFont, List[str]]:
    """从大到小试，找到能塞进 max_lines 行的字号。"""
    size = base_size
    while size > 12:
        f = _font(fonts, size)
        lines = _wrap_needed(draw, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 2
    f = _font(fonts, 12)
    return f, _wrap_needed(draw, text, f, max_w)


def render(bg: Image.Image, theme: Theme, colors: dict) -> Image.Image:
    W, H = bg.size
    img = bg.convert("RGBA")

    # 底部渐变遮罩，保证文字可读
    scrim = Image.new("L", (1, H), 0)
    top = int(H * 0.42)
    for y in range(H):
        if y < top:
            continue
        t = (y - top) / max(H - top - 1, 1)
        scrim.putpixel((0, y), int(200 * (t ** 1.4)))
    scrim = scrim.resize((W, H))
    scrim_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if colors["text_light"]:
        scrim_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        scrim_layer.putalpha(scrim)
        scrim_layer = Image.composite(Image.new("RGBA", (W, H), (8, 9, 14, 255)), scrim_layer, scrim)
    else:
        scrim_layer.putalpha(scrim)
        scrim_layer = Image.composite(Image.new("RGBA", (W, H), (250, 250, 252, 255)), scrim_layer, scrim)
    img = Image.alpha_composite(img, scrim_layer)

    draw = ImageDraw.Draw(img)
    margin = int(W * 0.085)
    max_w = W - margin * 2

    # ---- 主标题 ----
    title_font, title_lines = _fit_font(draw, theme.title, max_w,
                                        int(W * 0.15), 2, FONT_BOLD)
    line_h = int(title_font.size * 1.22)
    total = line_h * len(title_lines)
    y = H - margin - total - int(H * 0.10)

    # 强调线
    if colors["accent"]:
        draw.rectangle([margin, y - int(W * 0.045),
                        margin + int(W * 0.10), y - int(W * 0.045) + max(3, W // 200)],
                       fill=colors["accent"])

    for ln in title_lines:
        draw.text((margin, y), ln, font=title_font, fill=colors["text"])
        y += line_h

    # ---- 副标题 ----
    if theme.subtitle.strip():
        sub_font, sub_lines = _fit_font(draw, theme.subtitle, max_w,
                                        int(W * 0.052), 2, FONT_REG)
        for ln in sub_lines:
            draw.text((margin, y + int(H * 0.012)), ln, font=sub_font, fill=colors["sub"])
            y += int(sub_font.size * 1.3)

    # ---- 信息行 ----
    if theme.meta.strip():
        meta_font = _font(FONT_REG, max(14, int(W * 0.030)))
        draw.text((margin, H - margin - meta_font.size), theme.meta,
                  font=meta_font, fill=colors["sub"])

    return img.convert("RGB")


def make_poster(engine, theme: Theme, seed: int = 42,
                out_path: Optional[str] = None) -> Image.Image:
    bg = generate_bg(engine, theme, seed=seed)
    colors = analyze_colors(bg)
    poster = render(bg, theme, colors)

    # 2× 导出 + 轻锐化
    W, H = poster.size
    up = poster.resize((int(W * 2), int(H * 2)), Image.LANCZOS)
    up = up.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    if out_path:
        up.save(out_path)
    return up
