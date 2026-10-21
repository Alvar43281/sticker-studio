import io
p = r"D:\agent\poster-studio\app.py"
t = io.open(p, encoding="utf-8").read()

t = t.replace("from extra import rot_float_frames, sequence_frames, video_to_gif",
              "from extra import rot_float_frames, sequence_frames, video_to_gif\nfrom fx import FRAME_FX")

# 把画面动效并入下拉
t = t.replace('EFFECTS = {\n    "旋转悬浮": None,          # 特殊处理',
              'EFFECTS = {\n    "旋转悬浮": None,          # 特殊处理\n'
              '    "肯·伯恩斯": None, "波浪扭曲": None, "故障": None,\n'
              '    "光斑漂移": None, "万花筒": None,')

old = '''    if effect == "旋转悬浮":
        frames = rot_float_frames(rgba, n=24, bg=bg)
    else:
        frames = render_frames(rgba, effect, n=20, bg=bg, **EFFECTS.get(effect, {}))'''
new = '''    if effect == "旋转悬浮":
        frames = rot_float_frames(rgba, n=24, bg=bg)
    elif effect in FRAME_FX:
        a4 = rgba[..., 3:4].astype(np.float32) / 255.0
        base = (rgba[..., :3].astype(np.float32) * a4
                + np.array(bg, np.float32) * (1 - a4)).astype(np.uint8)
        frames = FRAME_FX[effect](base, n=24)
    else:
        frames = render_frames(rgba, effect, n=20, bg=bg, **EFFECTS.get(effect, {}))'''
assert old in t, "未找到动效分支"
t = t.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("patched app.py")
