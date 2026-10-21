import io, re
p = r"D:\agent\poster-studio\index.html"
t = io.open(p, encoding="utf-8").read()

# 1) 去掉数字统计
t = re.sub(r'\s*<div class="stats">.*?</div>\s*</div>\s*</header>', '\n  </div>\n</header>', t, flags=re.S)

# 2) 图片容器去掉白底/边框/阴影，让它和网页融为一体
t = re.sub(r'\.hero-media\{[^}]*\}', '', t, flags=re.S)
t = re.sub(r'\.hero-media img\{[^}]*\}', '', t, flags=re.S)
t = t.replace('section{padding:62px 0;border-top:1px solid var(--line)}',
              'section{padding:62px 0;border-top:1px solid var(--line)}\n'
              '.hero-media{width:250px;margin:20px auto 0;background:transparent;border:0}\n'
              '.hero-media img{display:block;width:100%;background:transparent}')

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("index.html 已更新")
