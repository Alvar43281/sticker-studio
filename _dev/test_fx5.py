from gradio_client import Client, handle_file
c = Client("http://127.0.0.1:7870", verbose=False)
for eff in ["极坐标展开","CRT","半调网点","老电影"]:
    r = c.predict(img=handle_file(r"D:\agent\poster-studio\meme\src_cat.png"),
                  border_name="无", bpx=9, top="", bottom="", effect=eff,
                  bg_name="白", no_cut=False, api_name="/do_sticker")
    print(eff, "→", r[1][1].split("\\")[-1])
