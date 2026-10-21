from gradio_client import Client, handle_file
c = Client("http://127.0.0.1:7870", verbose=False)
r = c.predict(img=handle_file(r"D:\agent\素材\奶龙_开心.png"),
              border_name="白色", bpx=9, top="奶龙", bottom="我来啦",
              effect="弹跳", bg_name="白", no_cut=False, api_name="/do_sticker")
print("输出文件:", [p.split("\\")[-1] for p in r[1]])
print(r[2])
