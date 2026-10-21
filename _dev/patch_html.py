import io
p = r"D:\agent\poster-studio\index.html"
t = io.open(p, encoding="utf-8").read()
block = """<section>
  <div class="wrap">
    <h2>热门表情包格式</h2>
    <p class="lead">套用流行文案与动效，一键出图。示例角色由 AI 生成，非官方素材。</p>
    <div class="cards">
      <article class="card">
        <div class="tag">CAT MEME</div>
        <h3>哈基米 · 弹跳</h3>
        <p>“哈基米”上下重复，配合纵向弹跳，节奏感强。</p>
        <img src="assets/meme_cat.webp" alt="猫 meme">
      </article>
      <article class="card">
        <div class="tag">KANGAROO</div>
        <h3>你的胆子 · 冲击</h3>
        <p>“你的胆子 / 肥嘟嘟的”两句反差文案，配回弹冲击。</p>
        <img src="assets/meme_roo.webp" alt="袋鼠梗">
      </article>
      <article class="card">
        <div class="tag">WORK</div>
        <h3>打工吧 · 流光</h3>
        <p>职场日常文案，配轮廓辉光与扫光，适合下班发。</p>
        <img src="assets/fx_glow.webp" alt="打工梗">
      </article>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>九种动效</h2>"""
old = """<section>
  <div class="wrap">
    <h2>九种动效</h2>"""
t = t.replace(old, block, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("html updated")
