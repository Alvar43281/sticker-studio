import io
from pathlib import Path

ROOT = Path(r"D:\agent\poster-studio")
APP = "http://127.0.0.1:7870"

NAV = [
    ("index.html", "首页"),
    ("fn_cutout.html", "抠图"),
    ("fn_sticker.html", "贴纸"),
    ("fn_emblem.html", "徽记"),
    ("fn_sequence.html", "序列"),
    ("fn_video.html", "视频转 GIF"),
]

BASE_CSS = """
:root{--bg:#0b0c10;--panel:#14161d;--panel2:#1a1d26;--text:#eef1f7;
  --sub:#9aa3b2;--line:#252a36;--accent:#6ea8fe;--accent2:#b388ff;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);line-height:1.7;
  font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;
  -webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.nav{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:6px;
  padding:10px 20px;background:rgba(11,12,16,.92);backdrop-filter:blur(10px);
  border-bottom:1px solid var(--line);flex-wrap:wrap}
.nav .brand{font-weight:700;letter-spacing:1px;margin-right:14px;
  background:linear-gradient(120deg,#fff,var(--accent));
  -webkit-background-clip:text;background-clip:text;color:transparent}
.nav a.lnk{padding:6px 12px;border-radius:9px;font-size:13.5px;color:var(--sub);
  border:1px solid transparent;transition:.2s}
.nav a.lnk:hover{color:var(--text);background:var(--panel);border-color:var(--line)}
.nav a.lnk.on{color:var(--accent);background:rgba(110,168,254,.12);
  border-color:rgba(110,168,254,.35)}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
section{padding:62px 0;border-top:1px solid var(--line)}
h2{font-size:25px;margin:0 0 8px}
.lead{color:var(--sub);margin:0 0 30px;font-size:15px}
.lead b{color:var(--text)}
"""

NAV_HTML = '<nav class="nav">\n  <span class="brand">贴纸工坊</span>\n'
for href, label in NAV:
    NAV_HTML += f'  <a class="lnk{{ON}}" href="{href}">{label}</a>\n'
NAV_HTML += "</nav>\n"


def nav(active="index.html"):
    html = NAV_HTML
    for href, _ in NAV:
        if href == active:
            html = html.replace(f'href="{href}"', f'href="{href}" class="on"', 1)
    html = html.replace("class=\"lnk{ON}\"", "class=\"lnk\"")
    # 修正：把 on 类加回去
    html = html.replace(f'<a class="lnk" href="{active}"',
                        f'<a class="lnk on" href="{active}"')
    return html


FUNC_PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 贴纸工坊</title>
<style>
{css}
body{{overflow:hidden}}
main{{height:calc(100vh - 53px);display:flex;flex-direction:column}}
#bar{{display:flex;align-items:center;gap:12px;padding:8px 20px;
  border-bottom:1px solid var(--line);font-size:13px;color:var(--sub);
  background:var(--panel)}}
#bar b{{color:var(--text)}}
#bar a{{color:var(--accent)}}
#tip{{margin:14px 20px;padding:12px 16px;border-radius:12px;font-size:13.5px;
  background:rgba(255,120,120,.08);border:1px solid rgba(255,120,120,.3);
  color:#ffb3b3;display:none}}
#iframe{{flex:1;width:100%;border:0;background:#0f1116}}
.loading{{position:absolute;inset:53px 0 0 0;display:flex;align-items:center;
  justify-content:center;color:var(--sub);font-size:14px;pointer-events:none}}
</style>
</head>
<body>
{nav}
<main>
  <div id="bar">
    <b>{title}</b>
    <span>{desc}</span>
    <span style="margin-left:auto">
      <a href="{app}/?tab={tab}" target="_blank">在新窗口打开 ↗</a>
    </span>
  </div>
  <div id="tip">
    连不上本地程序（{app}）。请先启动：<br>
    <code>cd D:\\agent\\poster-studio</code><br>
    <code>..\\sequence-evolver\\.venv\\Scripts\\python.exe app.py</code>
  </div>
  <iframe id="iframe" src="{app}/?tab={tab}" allow="clipboard-write"></iframe>
</main>
<script>
  const f = document.getElementById('iframe');
  const tip = document.getElementById('tip');
  let loaded = false;
  f.addEventListener('load', () => {{ loaded = true; tip.style.display = 'none'; }});
  setTimeout(() => {{ if (!loaded) tip.style.display = 'block'; }}, 4000);
  // 允许用 ?app=http://ip:port 覆盖地址
  const q = new URLSearchParams(location.search).get('app');
  if (q) {{ f.src = q + '/?tab={tab}'; }}
</script>
</body>
</html>
"""

FUNCS = [
    ("fn_cutout.html", "抠图", "cutout",
     "去背景，输出透明 PNG；可同时导出白底/深色底"),
    ("fn_sticker.html", "贴纸", "sticker",
     "抠图 + 描边 + 配文 + 19 种动效"),
    ("fn_emblem.html", "徽记", "emblem",
     "图标粒子汇聚 + 轮廓辉光 + 扫光定型"),
    ("fn_sequence.html", "序列", "sequence",
     "多图按顺序播放，可叠倒计时数字"),
    ("fn_video.html", "视频转 GIF", "video",
     "短视频截取片段转 GIF"),
]

for fname, title, tab, desc in FUNCS:
    html = FUNC_PAGE.format(title=title, desc=desc, tab=tab, app=APP,
                            nav=nav(fname), css=BASE_CSS)
    (ROOT / fname).write_text(html, encoding="utf-8")
    print("生成", fname)

# ---------------- 首页 ----------------
MODS = [
    ("fn_cutout.html", "01", "抠图", "去背景 → 透明 PNG，可附白底/深色底"),
    ("fn_sticker.html", "02", "贴纸", "抠图 + 描边 + 配文 + 动效"),
    ("fn_emblem.html", "03", "徽记", "图标粒子汇聚 + 辉光 + 扫光"),
    ("fn_sequence.html", "04", "序列", "多图按顺序播放 + 倒计时"),
    ("fn_video.html", "05", "视频转 GIF", "短视频截片段转 GIF"),
]

cards = ""
for href, no, name, desc in MODS:
    cards += f'''      <a class="mod" href="{href}">
        <div class="no">{no}</div>
        <h3>{name}</h3>
        <p>{desc}</p>
        <span class="go">进入 →</span>
      </a>
'''

index = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>贴纸工坊</title>
<style>
{BASE_CSS}
.hero{{padding:76px 0 54px;text-align:center;
  background:radial-gradient(900px 420px at 50% -10%,rgba(110,168,254,.18),transparent 60%),
  radial-gradient(700px 380px at 82% 8%,rgba(179,136,255,.14),transparent 60%)}}
.badge{{display:inline-block;padding:5px 14px;border-radius:999px;font-size:12px;
  color:var(--accent);border:1px solid rgba(110,168,254,.35);
  background:rgba(110,168,254,.08);letter-spacing:2px}}
h1{{font-size:50px;margin:16px 0 8px;letter-spacing:2px;
  background:linear-gradient(120deg,#fff 20%,var(--accent) 60%,var(--accent2));
  -webkit-background-clip:text;background-clip:text;color:transparent}}
.hero p{{color:var(--sub);font-size:16px;margin:0 auto 26px;max-width:560px}}
.stats{{display:flex;justify-content:center;gap:38px;flex-wrap:wrap;margin-top:26px}}
.stat b{{display:block;font-size:25px;color:var(--accent)}}
.stat span{{font-size:12.5px;color:var(--sub)}}
.mods{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px}}
.mod{{display:block;background:linear-gradient(180deg,var(--panel),var(--panel2));
  border:1px solid var(--line);border-radius:18px;padding:20px;transition:.25s}}
.mod:hover{{transform:translateY(-4px);border-color:rgba(110,168,254,.5)}}
.mod .no{{font-size:11.5px;color:var(--accent);letter-spacing:1.5px}}
.mod h3{{margin:4px 0 6px;font-size:17px}}
.mod p{{margin:0;color:var(--sub);font-size:13px}}
.mod .go{{display:inline-block;margin-top:12px;font-size:12.5px;color:var(--accent)}}
.note{{background:rgba(110,168,254,.07);border:1px solid rgba(110,168,254,.22);
  border-radius:12px;padding:14px 16px;color:var(--sub);font-size:13.5px}}
.note b{{color:var(--text)}}
pre{{background:#0e1016;border:1px solid var(--line);border-radius:12px;
  padding:14px 16px;overflow:auto;font-size:13px;color:#c9d3e4;
  font-family:Consolas,monospace}}
footer{{padding:44px 0;text-align:center;color:var(--sub);font-size:12.5px;
  border-top:1px solid var(--line)}}
</style>
</head>
<body>
{nav("index.html")}
<header class="hero">
  <div class="wrap">
    <div class="badge">课程设计 · 图像处理与动效</div>
    <h1>贴纸工坊</h1>
    <p>五个独立功能，点进去就能直接用。全部本地运行。</p>
    <div class="stats">
      <div class="stat"><b>5</b><span>功能</span></div>
      <div class="stat"><b>19</b><span>动效</span></div>
      <div class="stat"><b>5</b><span>抠图策略</span></div>
      <div class="stat"><b>0</b><span>网络依赖</span></div>
    </div>
  </div>
</header>

<section>
  <div class="wrap">
    <h2>功能入口</h2>
    <p class="lead">点击进入对应功能页，页面内嵌真实程序。</p>
    <div class="mods">
{cards}    </div>
    <p class="note" style="margin-top:22px">
      <b>使用前：</b>功能页需要本地程序在运行。没启动的话，页面会提示怎么启动。
    </p>
    <pre>cd D:\\agent\\poster-studio
..\\sequence-evolver\\.venv\\Scripts\\python.exe app.py</pre>
  </div>
</section>

<footer>
  <div class="wrap">贴纸工坊 · 本地图像处理与动效工具　|　素材仅用于课程作业演示</div>
</footer>
</body>
</html>
"""
(ROOT / "index.html").write_text(index, encoding="utf-8")
print("生成 index.html")
