from gradio_client import Client, handle_file
c = Client("http://127.0.0.1:7870", verbose=False)
r = c.predict(img=handle_file(r"D:\agent\poster-studio\meme\src_cat.png"),
              border_name="白色", bpx=9, top="哈基米", bottom="哈基米",
              effect="弹跳", bg_name="白", api_name="/do_sticker")
print("猫meme:", r[0].split("\\")[-1], "|", r[2])
