import io
p = r"D:\agent\poster-studio\app.py"
t = io.open(p, encoding="utf-8").read()

# 给 Tabs 和每个 Tab 加 id
t = t.replace('with gr.Tabs():', 'with gr.Tabs(selected="cutout") as tabs:')
t = t.replace('with gr.Tab("抠图"):', 'with gr.Tab("抠图", id="cutout"):')
t = t.replace('with gr.Tab("贴纸"):', 'with gr.Tab("贴纸", id="sticker"):')
t = t.replace('with gr.Tab("徽记"):', 'with gr.Tab("徽记", id="emblem"):')
t = t.replace('with gr.Tab("序列"):', 'with gr.Tab("序列", id="sequence"):')
t = t.replace('with gr.Tab("视频转 GIF"):', 'with gr.Tab("视频转 GIF", id="video"):')

# 支持 ?tab=xxx 自动切换
if "def _select_tab" not in t:
    hook = '''
def _select_tab(request: gr.Request):
    """URL 带 ?tab=cutout/sticker/emblem/sequence/video 时，自动切到对应功能。"""
    want = "cutout"
    try:
        want = (request.query_params.get("tab") or "cutout").lower()
    except Exception:
        pass
    valid = {"cutout", "sticker", "emblem", "sequence", "video"}
    return gr.update(selected=(want if want in valid else "cutout"))


'''
    t = t.replace("def build_ui():", hook + "def build_ui():", 1)
    t = t.replace("    return demo", "        demo.load(_select_tab, inputs=None, outputs=tabs)\n    return demo", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("app.py 已支持 ?tab= 参数")
