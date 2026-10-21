# 贴纸工坊 · Sticker Studio

> 一个本地运行的图像处理工具：**抠图 · 贴纸 · 徽记 · 序列 · 视频转 GIF** 五个并列功能，19 种动效。
> 纯 CPU 即可运行，不调用任何在线接口。

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)

---

## 功能

| 模块 | 输入 | 处理 | 输出 |
|---|---|---|---|
| **抠图** | 单张图片 | 去背景 → 裁边 → 居中 | 透明 PNG（可附白底/深色底） |
| **贴纸** | 单张图片 | 抠图 → 描边 → 配文 → 动效 | 透明 PNG + GIF + WebP |
| **徽记** | 图标/徽章 | 形状提取 → 粒子汇聚 → 辉光 → 扫光 | 透明 PNG + GIF + WebP |
| **序列** | 多张图片 | 顺序播放 + 交叉淡化 + 倒计时 | GIF + WebP |
| **视频转 GIF** | 短视频 | 截取片段 → 两遍调色板 | GIF |

### 19 种动效

- **主体动效（9）**：抖动、弹跳、冲击、摇摆、呼吸、果冻、流光、残影、崩解
- **特写（1）**：旋转悬浮（横向压扁 + 镜像模拟 3D 自转，投影随高度缩放）
- **画面动效（9）**：肯·伯恩斯、波浪扭曲、故障、光斑漂移、万花筒、极坐标展开、CRT、半调网点、老电影

> 画面动效只改像素与坐标，**不依赖主体轮廓**，任何素材都能用。

---

## 快速开始

```bash
git clone https://github.com/YOUR_NAME/sticker-studio.git
cd sticker-studio
pip install -r requirements.txt
python app.py
# 浏览器打开 http://127.0.0.1:7870
```

模型 `isnetis.onnx`（约 168MB）**首次运行会自动下载**；
也可手动放到 `models/isnetis.onnx`，或用环境变量指定：

```bash
export SEG_MODEL_PATH=/path/to/isnetis.onnx
export FFMPEG_PATH=/usr/bin/ffmpeg
```

---

## 技术栈

| 层 | 技术 |
|---|---|
| 图像处理 | OpenCV（重映射、形态学、GrabCut、颜色空间） |
| 分割推理 | ONNX Runtime + isnet-anime |
| 排版渲染 | Pillow |
| 编解码 | FFmpeg（GIF 两遍调色板、视频转码） |
| 界面 | Gradio 6 |

---

## 原理要点

### 抠图：五路自动择优

单一算法总有失效场景，所以并行尝试并挑选「主体占比 10%~82%」的合理结果：

| 策略 | 适用 |
|---|---|
| ONNX 分割模型 | 动漫人物 |
| 泛洪填充（`FLOODFILL_FIXED_RANGE`） | 纯色平背景 |
| 饱和度分离 | 彩色物体 + 灰白底 |
| 浅色背景规则 | 棋盘格 / 近白底 |
| GrabCut | 渐变柔和背景 |

都不理想时取覆盖率最接近 40% 的结果；再不行退回「整图加白框」模式。

### 动效：确定性 + 周期化

所有动效都是数学变换，没有生成模型，因此**同参数必得同结果**。
时间参数统一取 `2π` 的整数倍，保证 GIF 循环首尾衔接、不跳帧。

### GIF：两遍调色板

先用 `palettegen` 统计全片调色板，再 `paletteuse` 统一量化，
避免逐帧独立量化造成的颜色闪烁。同时输出体积约为 GIF 1/4 的动图 WebP。

---

## 目录结构

```
.
├── app.py          Gradio 界面与路由
├── sticker.py      抠图 / 贴纸化 / 配文 / 主体动效 / 编码
├── fx.py           9 种画面动效
├── extra.py        旋转悬浮 / 序列 / 视频转 GIF
├── logo.py         徽记粒子汇聚
├── assets/         演示素材
├── index.html      本地说明页
└── requirements.txt
```

---

## 已知限制

1. **复杂背景**：背景花纹紧贴主体时，分割模型可能把花纹算进主体
2. **低分辨率素材**：放大后偏糊
3. **半调网点较慢**：逐格画圆，24 帧约 3 秒
4. **不支持透明 GIF**：GIF 只有 1-bit 透明，需要透明请用 WebP
5. **非语义分割**：模型只认「像人/像主体」的区域，不区分头发、衣服、手臂

---

## 许可

代码使用 [MIT License](LICENSE)。

`assets/` 中的演示素材仅用于课程作业与学习交流，**不得商用**；
其中的卡通形象版权归原权利方所有。

---

## 致谢

- [isnet-anime](https://huggingface.co/skytnt/anime-seg) —— 动漫人物分割模型
- [OpenCV](https://opencv.org/) · [Gradio](https://gradio.app/) · [FFmpeg](https://ffmpeg.org/)
