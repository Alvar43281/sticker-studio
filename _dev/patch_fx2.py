import io
p = r"D:\agent\poster-studio\app.py"
t = io.open(p, encoding="utf-8").read()
old = '    "肯·伯恩斯": None, "波浪扭曲": None, "故障": None,\n    "光斑漂移": None, "万花筒": None,'
new = ('    "肯·伯恩斯": None, "波浪扭曲": None, "故障": None,\n'
       '    "光斑漂移": None, "万花筒": None, "极坐标展开": None,\n'
       '    "CRT": None, "半调网点": None, "老电影": None,')
assert old in t
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("app.py 动效列表已扩展")
