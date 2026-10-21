from gradio_client import Client, handle_file
c = Client("http://127.0.0.1:7870", verbose=False)
base = dict(img=handle_file(r"D:\agent\poster-studio\meme\src_cat.png"),
            border_name="无", bpx=9, top="", bottom="", bg_name="白", no_cut=False)
for eff in ["肯·伯恩斯","波浪扭曲","故障","光斑漂移","万花筒"]:
    r = c.predict(**base, effect=eff, api_name="/do_sticker")
    print(f"{eff:6s} →", [p.split('\\')[-1] for p in r[1]])
