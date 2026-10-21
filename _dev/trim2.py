import re
from pathlib import Path
NET = Path(r"D:\agent\deploy\netlify")
h = (NET/"index.html").read_text(encoding="utf-8")
used = set(re.findall(r'assets/([^"]+)', h))
removed, failed = 0, []
for f in list((NET/"assets").iterdir()):
    if f.name not in used:
        try:
            f.unlink(); removed += 1
        except Exception as e:
            failed.append(f.name)
total = sum(f.stat().st_size for f in NET.rglob("*") if f.is_file())
print(f"删除 {removed} 个，失败 {len(failed)} 个")
print(f"站点 {total/1024/1024:.2f} MB，保留素材 {len(used)} 个")
if failed: print("失败文件:", failed[:5])
