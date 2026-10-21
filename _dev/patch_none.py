import io
p = r"D:\agent\poster-studio\app.py"
t = io.open(p, encoding="utf-8").read()
old = '''    progress(0.65, desc="动效…")
    bg = (255, 255, 255) if bg_name == "白" else (18, 18, 22)'''
new = '''    if effect == "无":
        return str(png), [str(png)], "透明 PNG（静态，无动效）"

    progress(0.65, desc="动效…")
    bg = (255, 255, 255) if bg_name == "白" else (18, 18, 22)'''
assert old in t
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("已插入「无动效」分支")
