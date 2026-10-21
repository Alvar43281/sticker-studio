import io
p = r"D:\agent\poster-studio\sticker.py"
t = io.open(p, encoding="utf-8").read()

# FFmpeg：找不到时退回 imageio-ffmpeg 自带二进制（云端常见）
old = '''    return shutil.which("ffmpeg") or "ffmpeg"'''
new = '''    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"'''
t = t.replace(old, new, 1)

# 模型缺失时自动从 HuggingFace 拉（云端部署用）
old2 = '''def _session():
    global _seg
    if _seg is None:
        import onnxruntime as ort
        _seg = ort.InferenceSession(SEG_MODEL, providers=["CPUExecutionProvider"])
    return _seg'''
new2 = '''def _ensure_model(path: str) -> str:
    """模型不存在时尝试从 HuggingFace 拉取（云端首次启动用）。"""
    if Path(path).exists():
        return path
    try:
        from huggingface_hub import hf_hub_download
        fp = hf_hub_download("skytnt/anime-seg", "isnetis.onnx")
        return fp
    except Exception:
        return path


def _session():
    global _seg
    if _seg is None:
        import onnxruntime as ort
        _seg = ort.InferenceSession(_ensure_model(SEG_MODEL),
                                    providers=["CPUExecutionProvider"])
    return _seg'''
assert old2 in t
t = t.replace(old2, new2, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("已加：FFmpeg 回退 + 模型自动下载")
