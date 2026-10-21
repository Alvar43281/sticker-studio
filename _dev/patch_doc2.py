import io
p = r"D:\agent\poster-studio\功能总览.md"
t = io.open(p, encoding="utf-8").read()
t = t.replace("| 模板 | 猫 meme（哈基米）、袋鼠（胆子肥嘟嘟）、奶龙、打工 |",
              "| 文字位置 | 上方 / 下方 / 上下 三种，单行文字自动适配字号与换行 |")
if "| 配文 |" in t:
    t = t.replace("| 配文 | 上下两行，字号自适应、自动换行、描边 |",
                  "| 配文 | 单个输入框 + 位置选择（上 / 下 / 上下），字号自适应、自动换行、描边 |")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("文档已同步")
