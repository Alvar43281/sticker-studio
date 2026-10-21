import re, shutil
from pathlib import Path
NET = Path(r"D:\agent\deploy\netlify")
h = (NET/"index.html").read_text(encoding="utf-8")
used = set(re.findall(r'assets/([^"]+)', h))
removed = 0
for f in (NET/"assets").iterdir():
    if f.name not in used:
        f.unlink(); removed += 1
total = sum(f.stat().st_size for f in NET.rglob("*") if f.is_file())
print(f"清理未引用素材 {removed} 个；站点现在 {total/1024/1024:.2f} MB，保留 {len(used)} 个")
