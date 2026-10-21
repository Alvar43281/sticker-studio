import io, re
p = r"D:\agent\poster-studio\index.html"
t = io.open(p, encoding="utf-8").read()
cards = """<section>
  <div class="wrap">
    <h2>成品示例</h2>
    <p class="lead">真实素材跑通的结果：主输出是<b>透明背景 PNG</b>，动图只是附加。<br>
    素材仅用于课程作业演示，非商业用途。</p>
    <div class="grid">
      <div class="fx" style="background:#f5f6f8"><img src="assets/ex_kangaroo_w.png" alt=""><b>你的胆子</b><span>肥嘟嘟的 · 冲击</span></div>
      <div class="fx" style="background:#f5f6f8"><img src="assets/ex_nailong_happy_w.png" alt=""><b>奶龙</b><span>我来啦 · 弹跳</span></div>
      <div class="fx" style="background:#f5f6f8"><img src="assets/ex_nailong_sleep_w.png" alt=""><b>奶龙</b><span>困了 · 呼吸</span></div>
      <div class="fx" style="background:#f5f6f8"><img src="assets/ex_hajimi_w.png" alt=""><b>哈基米</b><span>整图白框 · 抖动</span></div>
      <div class="fx" style="background:#f5f6f8"><img src="assets/ex_laugh_w.png" alt=""><b>哈哈</b><span>笑死我了 · 果冻</span></div>
    </div>
  </div>
</section>
"""
# 用新板块替换旧的「热门表情包格式」整节
start = t.index("<h2>热门表情包格式</h2>")
sec_start = t.rindex("<section>", 0, start)
sec_end = t.index("</section>", start) + len("</section>") + 1
t = t[:sec_start] + cards + t[sec_end:]
# 同时替换掉旧的 meme 卡（如果有）
t = t.replace("assets/meme_cat.webp", "assets/ex_hajimi_w.png").replace("assets/meme_roo.webp", "assets/ex_kangaroo_w.png")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("html updated")
