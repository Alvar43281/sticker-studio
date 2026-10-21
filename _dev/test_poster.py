import sys, time
sys.path.insert(0, r"D:\agent\sequence-evolver")
from pathlib import Path
from core import Engine
from poster import Theme, make_poster

root = Path(r"D:\agent\poster-studio")
engine = Engine(r"D:\agent\sequence-evolver\models\sd15-fp16")

jobs = [
    Theme(title="夏日音乐节", subtitle="SUMMER MUSIC FESTIVAL",
          meta="2026.08.12 - 08.14   城市公园", keywords="sunset stage, crowd silhouette, warm light",
          style="霓虹", ratio="3:4"),
    Theme(title="山间茶事", subtitle="一席一世界", meta="春日限定",
          keywords="misty mountain, tea ceremony, soft morning light", style="国风", ratio="3:4"),
]
for i, t in enumerate(jobs):
    t0 = time.time()
    p = make_poster(engine, t, seed=100+i, out_path=str(root/f"sample_{i+1}.png"))
    print(f"海报 {i+1}: {t.title}  {p.size}  {time.time()-t0:.0f}s")
