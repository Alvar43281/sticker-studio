import io
p = r"D:\agent\poster-studio\功能总览.md"
t = io.open(p, encoding="utf-8").read()

t = t.replace("## 一、四个功能模块", "## 一、五个功能模块（网页上按标签页并列）")
old_tbl_start = t.index("| 模块 | 输入 | 处理 | 输出 |")
old_tbl_end = t.index("\n\n", old_tbl_start)
new_tbl = """| 模块 | 输入 | 处理 | 输出 |
|---|---|---|---|
| **抠图** | 单张图片 | 去背景 → 裁边 → 居中 | 透明 PNG（可附白底/深色底） |
| **贴纸** | 单张图片 | 抠图 → 描边 → 配文 → 动效 | 透明 PNG + GIF + WebP |
| **徽记** | 图标/徽章 | 形状提取 → 粒子汇聚 → 辉光 → 扫光 | 透明 PNG + GIF + WebP |
| **序列** | 多张图片（按顺序） | 逐张播放 + 交叉淡化 + 可选倒计时 | GIF + WebP |
| **视频转 GIF** | 短视频（MP4 等） | 截取片段 → 两遍调色板编码 | GIF |"""
t = t[:old_tbl_start] + new_tbl + t[old_tbl_end:]

t = t.replace("主输出：透明背景 PNG；另附 GIF / WebP 动图。",
              "五个功能并列，各自独立可用。")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("功能总览已更新为五个模块")
