import io, re
p = r"D:\agent\poster-studio\app.py"
t = io.open(p, encoding="utf-8").read()
t = re.sub(r'\nTEMPLATES = \{.*?\n\}\n', '\n', t, flags=re.S)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("TEMPLATES 已删除")
