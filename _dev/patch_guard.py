import io
p = r"D:\agent\poster-studio\app.py"
t = io.open(p, encoding="utf-8").read()
if "def _port_free" not in t:
    guard = '''

def _port_free(port: int) -> bool:
    import socket
    s = socket.socket()
    try:
        s.bind(("0.0.0.0", port))
        return True
    except OSError:
        return False
    finally:
        s.close()

'''
    t = t.replace("def build_ui():", guard + "def build_ui():", 1)
    t = t.replace('''if __name__ == "__main__":
    app = build_ui()''', '''if __name__ == "__main__":
    if not _port_free(7870):
        raise SystemExit("端口 7870 已被占用 —— 先关掉旧的实例再启动。")
    app = build_ui()''', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("已加入端口占用保护")
