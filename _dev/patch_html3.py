import io, re
p = r"D:\agent\poster-studio\index.html"
t = io.open(p, encoding="utf-8").read()

new_mods = '''    <div class="mods">
      <article class="mod">
        <img src="assets/mod_cutout.png" alt="">
        <div class="body"><div class="no">01</div><h3>抠图</h3>
          <p>去背景，输出透明 PNG；可同时导出白底、深色底版本。</p></div>
      </article>
      <article class="mod">
        <img src="assets/mod_sticker.png" alt="">
        <div class="body"><div class="no">02</div><h3>贴纸</h3>
          <p>抠图 → 描边 → 配文 → 动效，输出透明 PNG + GIF/WebP。</p></div>
      </article>
      <article class="mod">
        <img src="assets/emblem_still.png" alt="">
        <div class="body"><div class="no">03</div><h3>徽记</h3>
          <p>图标粒子汇聚 + 轮廓辉光 + 扫光定型。</p></div>
      </article>
      <article class="mod">
        <img src="assets/mod_seq.png" alt="">
        <div class="body"><div class="no">04</div><h3>序列</h3>
          <p>多图按顺序播放，自动叠加 3→2→1 倒计时。</p></div>
      </article>
      <article class="mod">
        <img src="assets/mod_video.png" alt="">
        <div class="body"><div class="no">05</div><h3>视频转 GIF</h3>
          <p>短视频截取片段转 GIF，可调帧率、宽度、起点、时长。</p></div>
      </article>
    </div>'''

start = t.index('<div class="mods">')
end = t.index('</div>', t.index('MODULE 05') if 'MODULE 05' in t else t.index('视频转 GIF', start))
# 更稳妥：从 mods 起点到该 div 的闭合（用已知结束标记）
m_end = t.index('</div>\n  </div>\n</section>', start) + len('</div>')
t = t[:start] + new_mods + t[m_end:]

# 更新首屏措辞（并列）
t = t.replace("五个并列功能：抠图、贴纸、徽记、序列、视频转 GIF。",
              "五个并列功能：抠图 · 贴纸 · 徽记 · 序列 · 视频转 GIF。")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("模块顺序已对齐标签页")
