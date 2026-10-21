import io
p = r"D:\agent\poster-studio\app.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace('border = gr.Dropdown(list(BORDERS), value="白色", label="描边")',
              'border = gr.Dropdown(list(BORDERS), value="无", label="描边")')
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("默认描边 -> 无")
