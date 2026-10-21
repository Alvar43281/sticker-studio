import io
p = r"D:\agent\poster-studio\app.py"
t = io.open(p, encoding="utf-8").read()
block = """        def apply_tmpl(name):
            v = TEMPLATES.get(name)
            if not v:
                return gr.update(), gr.update(), gr.update(), gr.update()
            return (gr.update(value=v["top"]), gr.update(value=v["bottom"]),
                    gr.update(value=v["effect"]), gr.update(value=v["border"]))

        tmpl.change(apply_tmpl, inputs=tmpl,
                    outputs=[top, bottom, effect, border])

        btn_s.click(do_sticker,"""
t = t.replace("        btn_s.click(do_sticker,", block, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("patched + syntax OK")
