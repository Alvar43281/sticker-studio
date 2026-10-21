import io, re
from pathlib import Path
R = Path(r"D:\agent\poster-studio")

# ---------- 1) 首页：去掉五张示例图 ----------
idx = R/"index.html"
t = io.open(idx, encoding="utf-8").read()
t = re.sub(r'\s*<img src="assets/(ex5_[^"]+|emblem_still\.png|nugget_spin\.webp)" alt="">', '', t)
io.open(idx, "w", encoding="utf-8", newline="\n").write(t)
print("首页示例图已移除，剩余 img:", len(re.findall(r'<img ', t)))

# ---------- 2) 功能页：各加一条示例 ----------
DEMOS = {
  "fn_cutout.html":   ("assets/ex5_cutout.png",   "示例 · 奶龙抠图：棋盘格处为透明区域"),
  "fn_sticker.html":  ("assets/ex5_sticker.png",  "示例 · 奶龙贴纸：白边 + 配文"),
  "fn_emblem.html":   ("assets/emblem_still.png", "示例 · 徽记：粒子汇聚后定型"),
  "fn_sequence.html": ("assets/ex5_sequence.png", "示例 · 序列：3-2-1 倒计时"),
  "fn_video.html":    ("assets/nugget_spin.webp", "示例 · 视频转 GIF：旋转鸡块"),
}
CSS = """
#demo{display:flex;align-items:center;gap:14px;padding:10px 20px;
  border-bottom:1px solid var(--line);background:var(--panel2)}
#demo img{height:110px;width:110px;object-fit:contain;border-radius:12px;background:#fff}
#demo span{font-size:12.8px;color:var(--sub)}
#demo b{color:var(--text);font-size:13.2px;display:block;margin-bottom:2px}
"""
for fname, (img, cap) in DEMOS.items():
    f = R/fname
    h = io.open(f, encoding="utf-8").read()
    if "#demo{" not in h:
        h = h.replace("</style>", CSS + "</style>")
    if 'id="demo"' not in h:
        block = ('  <div id="demo">\n'
                 f'    <img src="{img}" alt="">\n'
                 f'    <span><b>这个功能在做什么</b>{cap}</span>\n'
                 '  </div>\n')
        h = h.replace('  <iframe id="iframe"', block + '  <iframe id="iframe"')
    io.open(f, "w", encoding="utf-8", newline="\n").write(h)
    print("已加示例:", fname)
