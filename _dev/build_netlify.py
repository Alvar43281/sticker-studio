import shutil
from pathlib import Path

SRC = Path(r"D:\agent\poster-studio")
NET = Path(r"D:\agent\deploy\netlify")
NET.mkdir(parents=True, exist_ok=True)
(NET / "assets").mkdir(exist_ok=True)

# 复制展示所需素材
for f in (SRC / "assets").glob("*"):
    if f.suffix.lower() in (".webp", ".png") and f.is_file():
        shutil.copy2(f, NET / "assets" / f.name)
print("素材复制:", len(list((NET/'assets').iterdir())), "个")

FX = [
    ("fx_shake", "抖动", "正弦位移 + 微旋"),
    ("fx_bounce", "弹跳", "纵向弹起 + 压扁"),
    ("fx_punch", "冲击", "回弹缓动放大"),
    ("fx_wobble", "摇摆", "绕轴往复旋转"),
    ("fx_breathe", "呼吸", "缓慢缩放"),
    ("fx_jelly", "果冻", "逐行正弦位移场"),
    ("fx_glow", "流光", "外发光 + 扫光"),
    ("fx_trail", "残影", "帧缓冲衰减"),
    ("fx_burst", "崩解", "边缘粒子飞散"),
    ("fx_rotate", "旋转悬浮", "自转 + 投影"),
    ("fx_kenburns", "肯·伯恩斯", "缓动推镜"),
    ("fx_wave", "波浪扭曲", "正弦位移场"),
    ("fx_glitch", "故障", "通道错位 + 横条"),
    ("fx_bokeh", "光斑漂移", "高斯光斑游走"),
    ("fx_kaleido", "万花筒", "极坐标折叠"),
    ("fx_polar", "极坐标展开", "卷成环并旋转"),
    ("fx_crt", "CRT", "扫描线 + 滚动带"),
    ("fx_halftone", "半调网点", "点径呼吸"),
    ("fx_oldfilm", "老电影", "棕褐 + 颗粒 + 划痕"),
]
fx_html = "\n".join(
    f'      <div class="fx"><img src="assets/{k}.webp" alt="{n}" loading="lazy">'
    f'<b>{n}</b><span>{d}</span></div>' for k, n, d in FX)

MODS = [
    ("ex5_cutout.png", "01", "抠图", "去背景输出透明 PNG；五路策略自动择优"),
    ("ex5_sticker.png", "02", "贴纸", "抠图 + 描边 + 配文 + 19 种动效"),
    ("emblem_still.png", "03", "徽记", "图标粒子汇聚 + 辉光 + 扫光定型"),
    ("ex5_sequence.png", "04", "序列", "多图顺序播放 + 倒计时数字"),
    ("nugget_spin.webp", "05", "视频转 GIF", "短视频截取片段转 GIF"),
]
mod_html = "\n".join(
    f'''      <article class="mod">
        <img src="assets/{img}" alt="{name}" loading="lazy">
        <div class="body"><div class="no">{no}</div><h3>{name}</h3><p>{desc}</p></div>
      </article>''' for img, no, name, desc in MODS)

HTML = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>贴纸工坊 · Sticker Studio</title>
<meta name="description" content="抠图、贴纸、徽记、序列、视频转 GIF —— 五个并列功能，19 种动效，全部本地推理。">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎨</text></svg>">
<style>
  :root{{--bg:#0b0c10;--panel:#14161d;--panel2:#1a1d26;--text:#eef1f7;
    --sub:#9aa3b2;--line:#252a36;--accent:#6ea8fe;--accent2:#b388ff}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--text);line-height:1.75;
    font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;
    -webkit-font-smoothing:antialiased}}
  a{{color:inherit;text-decoration:none}}
  .wrap{{max-width:1100px;margin:0 auto;padding:0 24px}}
  section{{padding:66px 0;border-top:1px solid var(--line)}}
  h2{{font-size:26px;margin:0 0 8px}}
  .lead{{color:var(--sub);margin:0 0 30px;font-size:15px}}
  .lead b{{color:var(--text)}}

  .hero{{padding:82px 0 56px;text-align:center;
    background:radial-gradient(900px 420px at 50% -10%,rgba(110,168,254,.18),transparent 60%),
    radial-gradient(700px 380px at 82% 8%,rgba(179,136,255,.14),transparent 60%)}}
  .badge{{display:inline-block;padding:5px 14px;border-radius:999px;font-size:12px;
    color:var(--accent);border:1px solid rgba(110,168,254,.35);
    background:rgba(110,168,254,.08);letter-spacing:2px}}
  h1{{font-size:52px;margin:16px 0 8px;letter-spacing:2px;
    background:linear-gradient(120deg,#fff 20%,var(--accent) 60%,var(--accent2));
    -webkit-background-clip:text;background-clip:text;color:transparent}}
  .hero p{{color:var(--sub);font-size:16px;margin:0 auto;max-width:600px}}
  .hero-media{{width:230px;margin:20px auto 0}}
  .hero-media img{{width:100%;display:block}}
  .cta{{margin-top:30px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap}}
  .btn{{display:inline-block;padding:11px 22px;border-radius:12px;font-size:14px;
    border:1px solid var(--line);background:var(--panel);color:var(--text);transition:.2s}}
  .btn:hover{{border-color:rgba(110,168,254,.6);transform:translateY(-2px)}}
  .btn.primary{{background:linear-gradient(135deg,#4874cb,#6ea8fe);border:0;
    color:#fff;font-weight:600}}

  .mods{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px}}
  .mod{{background:linear-gradient(180deg,var(--panel),var(--panel2));
    border:1px solid var(--line);border-radius:18px;overflow:hidden;transition:.25s}}
  .mod:hover{{transform:translateY(-4px);border-color:rgba(110,168,254,.5)}}
  .mod img{{width:100%;aspect-ratio:1/1;object-fit:contain;background:#fff;display:block}}
  .mod .body{{padding:14px 16px 18px}}
  .mod .no{{font-size:11px;color:var(--accent);letter-spacing:1.5px}}
  .mod h3{{margin:4px 0 6px;font-size:16.5px}}
  .mod p{{margin:0;color:var(--sub);font-size:12.8px}}

  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}}
  .fx{{background:var(--panel);border:1px solid var(--line);border-radius:13px;
    padding:9px;text-align:center;transition:.2s}}
  .fx:hover{{border-color:rgba(179,136,255,.5);transform:translateY(-3px)}}
  .fx img{{width:100%;border-radius:9px;display:block;background:#fff}}
  .fx b{{display:block;margin-top:8px;font-size:13px}}
  .fx span{{font-size:11px;color:var(--sub);display:block;line-height:1.4}}

  table{{width:100%;border-collapse:collapse;font-size:13.5px}}
  th,td{{text-align:left;padding:11px 13px;border-bottom:1px solid var(--line)}}
  th{{color:var(--sub);font-weight:500;font-size:12.5px}}
  td code{{color:var(--accent);font-family:Consolas,monospace;font-size:12.4px}}
  pre{{background:#0e1016;border:1px solid var(--line);border-radius:12px;
    padding:15px 17px;overflow:auto;font-size:12.8px;color:#c9d3e4;
    font-family:Consolas,monospace}}
  footer{{padding:44px 0;text-align:center;color:var(--sub);font-size:12.5px;
    border-top:1px solid var(--line)}}
  .pill{{display:inline-block;margin:0 5px;padding:4px 10px;border-radius:999px;
    background:var(--panel);border:1px solid var(--line);font-size:12px;color:var(--sub)}}
</style>
</head>
<body>

<header class="hero">
  <div class="wrap">
    <div class="badge">开源 · 本地运行 · MIT License</div>
    <h1>贴纸工坊</h1>
    <p>抠图 · 贴纸 · 徽记 · 序列 · 视频转 GIF　——　五个并列功能，19 种动效，全部本地推理。</p>
    <div class="hero-media"><img src="assets/nugget_spin.webp" alt="旋转悬浮"></div>
    <div class="cta">
      <a class="btn primary" href="#try">在线体验</a>
      <a class="btn" href="#features">看看功能</a>
      <a class="btn" href="#deploy">本地部署</a>
    </div>
  </div>
</header>

<section id="features">
  <div class="wrap">
    <h2>五个并列功能</h2>
    <p class="lead">网页顶部标签页切换，每个功能独立可用，没有主次之分。</p>
    <div class="mods">
{mod_html}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>19 种动效</h2>
    <p class="lead">
      主体动效 9 种作用在抠出的主体上；画面动效 9 种与旋转悬浮作用于整帧，
      <b>不依赖主体轮廓，任何素材都能用</b>。
    </p>
    <div class="grid">
{fx_html}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>技术栈</h2>
    <table>
      <tr><th>层</th><th>技术</th><th>用途</th></tr>
      <tr><td>图像处理</td><td>OpenCV 5</td><td>重映射、形态学、GrabCut、颜色空间</td></tr>
      <tr><td>分割推理</td><td>ONNX Runtime + isnet-anime</td><td>人物 / 背景分离（168MB 模型）</td></tr>
      <tr><td>排版渲染</td><td>Pillow</td><td>文字排版、描边、合成</td></tr>
      <tr><td>编解码</td><td>FFmpeg</td><td>GIF 双遍调色板、视频转码</td></tr>
      <tr><td>界面</td><td>Gradio 6</td><td>网页服务、上传、预览、下载</td></tr>
    </table>
  </div>
</section>

<section id="try">
  <div class="wrap">
    <h2>在线体验</h2>
    <p class="lead">
      完整程序运行在 Hugging Face Spaces（CPU 免费额度即可，本程序无需 GPU）。
    </p>
    <div class="cta" style="justify-content:flex-start">
      <a class="btn primary" href="https://huggingface.co/spaces/YOUR_NAME/sticker-studio" target="_blank" rel="noopener">
        🚀 打开在线演示
      </a>
      <a class="btn" href="https://github.com/YOUR_NAME/sticker-studio" target="_blank" rel="noopener">
        ⭐ GitHub 源码
      </a>
    </div>
    <p class="lead" style="margin-top:16px">
      <b>注意：</b>请把上面两个链接里的 <code>YOUR_NAME</code> 换成你自己的账号名。
    </p>
  </div>
</section>

<section id="deploy">
  <div class="wrap">
    <h2>本地部署</h2>
    <pre>git clone https://github.com/YOUR_NAME/sticker-studio.git
cd sticker-studio
pip install -r requirements.txt
python app.py            # 打开 http://127.0.0.1:7870</pre>
    <p class="lead" style="margin-top:18px">
      模型首次启动会自动下载（约 168MB）；也可手动放到 <code>models/isnetis.onnx</code>。
    </p>
  </div>
</section>

<footer>
  <div class="wrap">
    <div>
      <span class="pill">Python 3.11</span>
      <span class="pill">OpenCV</span>
      <span class="pill">ONNX Runtime</span>
      <span class="pill">FFmpeg</span>
      <span class="pill">Gradio</span>
      <span class="pill">MIT</span>
    </div>
    <p style="margin-top:16px">贴纸工坊 · Sticker Studio　|　素材仅用于课程作业演示</p>
  </div>
</footer>

</body>
</html>
"""
(NET / "index.html").write_text(HTML, encoding="utf-8")
print("Netlify 站点生成:", (NET / "index.html").stat().st_size // 1024, "KB")
