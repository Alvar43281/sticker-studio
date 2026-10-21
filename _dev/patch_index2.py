import io, re
p = r"D:\agent\poster-studio\index.html"
t = io.open(p, encoding="utf-8").read()

# 1) 删掉「使用前」提示与代码块
t = re.sub(r'\s*<p class="note" style="margin-top:22px">.*?</p>', '', t, flags=re.S)
t = re.sub(r'\s*<pre>.*?</pre>', '', t, flags=re.S)

# 2) 首屏加麦乐鸡旋转演示
t = t.replace('<p>五个独立功能，点进去就能直接用。全部本地运行。</p>',
              '<p>五个独立功能，点进去就能直接用。全部本地运行。</p>\n'
              '    <div class="hero-media"><img src="assets/nugget_spin.webp" alt="旋转悬浮"></div>')

# 3) 补 CSS
if '.hero-media{' not in t:
    t = t.replace('section{padding:62px 0;border-top:1px solid var(--line)}',
                  'section{padding:62px 0;border-top:1px solid var(--line)}\n'
                  '.hero-media{width:220px;margin:26px auto 4px;border-radius:22px;overflow:hidden;\n'
                  '  border:1px solid var(--line);background:var(--panel);\n'
                  '  box-shadow:0 24px 60px rgba(0,0,0,.5)}\n'
                  '.hero-media img{display:block;width:100%}')

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("index.html 已更新")
