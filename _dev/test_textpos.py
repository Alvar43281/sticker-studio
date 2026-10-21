from gradio_client import Client, handle_file
c = Client("http://127.0.0.1:7870", verbose=False)
info = c.view_api(return_format="dict")
print("贴纸端点参数:", [p["parameter_name"] for p in info["named_endpoints"]["/do_sticker"]["parameters"]])
for pos in ("上方","下方","上下"):
    r = c.predict(img=handle_file(r"D:\agent\素材\奶龙_开心.png"), border_name="无", bpx=9,
                  text="测试文字", text_pos=pos, effect="弹跳", bg_name="白", no_cut=False,
                  api_name="/do_sticker")
    print(f"  位置={pos} ->", r[1][0].split("\\")[-1], "|", r[2].split("|")[0].strip())
