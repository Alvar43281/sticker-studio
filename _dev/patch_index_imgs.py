import io, re
p = r"D:\agent\poster-studio\index.html"
t = io.open(p, encoding="utf-8").read()

# 每个功能卡插入示例图
imgs = {
  "fn_cutout.html":   "ex5_cutout.png",
  "fn_sticker.html":  "ex5_sticker.png",
  "fn_emblem.html":   "assets/emblem_still.png",
  "fn_sequence.html": "ex5_sequence.png",
  "fn_video.html":    "nugget_spin.webp",
}
for href, img in imgs.items():
    src = img if img.startswith("assets/") else "assets/" + img
    # 在 <a class="mod" href="X"> 之后插入 img
    pat = re.compile(r'(<a class="mod" href="' + re.escape(href) + r'">\s*)')
    t = pat.sub(r'\1\n        <img src="' + src + r'" alt="">', t, count=1)

# 卡片图片样式
if '.mod img{' not in t:
    t = t.replace('.mod .no{',
                  '.mod img{width:100%;aspect-ratio:1/1;object-fit:contain;'
                  'border-radius:12px;margin-bottom:12px;background:#fff;display:block}\n'
                  '.mod .no{')

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("index.html 已加入五张示例图")
