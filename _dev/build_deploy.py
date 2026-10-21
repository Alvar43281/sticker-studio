import io
import shutil
from pathlib import Path

SRC = Path(r"D:\agent\poster-studio")
DEP = Path(r"D:\agent\deploy")
shutil.rmtree(DEP, ignore_errors=True)
(DEP / "github").mkdir(parents=True)
(DEP / "hf-space").mkdir(parents=True)
(DEP / "netlify").mkdir(parents=True)

# ---------------- 1) HF Space 代码 ----------------
for f in ["app.py", "sticker.py", "fx.py", "extra.py", "logo.py"]:
    shutil.copy2(SRC / f, DEP / "hf-space" / f)

(DEP / "hf-space" / "requirements.txt").write_text(
    "gradio==6.30.0\n"
    "opencv-python-headless\n"
    "numpy\n"
    "pillow\n"
    "onnxruntime\n"
    "imageio-ffmpeg\n"
    "huggingface_hub\n",
    encoding="utf-8")

(DEP / "hf-space" / "packages.txt").write_text(
    "ffmpeg\nfonts-noto-cjk\n", encoding="utf-8")

(DEP / "hf-space" / "README.md").write_text("""---
title: 贴纸工坊
emoji: 🎨
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 6.30.0
app_file: app.py
pinned: false
license: mit
---

# 贴纸工坊 · Sticker Studio

抠图 / 贴纸 / 徽记 / 序列 / 视频转 GIF —— 五个并列功能，19 种动效，全部本地推理。

- 抠图：ONNX Runtime + isnet-anime，另有泛洪填充 / 饱和度分离 / 浅色背景 / GrabCut 共五路自动择优
- 贴纸：描边、配文（自由定位）、19 种动效
- 徽记：图标粒子汇聚 + 辉光 + 扫光
- 序列：多图顺序播放 + 倒计时
- 视频转 GIF：ffmpeg 两遍调色板

模型首次启动时自动从 `skytnt/anime-seg` 下载（约 168MB）。
""", encoding="utf-8")

# ---------------- 2) GitHub 仓库文件 ----------------
(DEP / "github" / "LICENSE").write_text("""MIT License

Copyright (c) 2026 杨健

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""", encoding="utf-8")

(DEP / "github" / ".gitignore").write_text("""# 环境
.venv/
venv/
__pycache__/
*.pyc

# 模型（体积大，不入库）
models/
*.onnx

# 产物
out/
artifacts/
*.gif
*.webp
*.mp4
!assets/*.gif
!assets/*.webp

# 系统
.DS_Store
Thumbs.db
""", encoding="utf-8")

print("部署骨架已建：", DEP)
