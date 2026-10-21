from gradio_client import Client, handle_file
c = Client("http://127.0.0.1:7870", verbose=False)
r = c.predict(img=handle_file(r"D:\agent\poster-studio\assets\sample_char.png"),
              border_name="白色", bpx=9, top="打工吧", bottom="今天也是",
              effect="果冻", bg_name="白", api_name="/do_sticker")
print("贴纸 OK:", r[0].split("\\")[-1], "|", r[2])
r2 = c.predict(img=handle_file(r"D:\agent\poster-studio\assets\sample_emblem.png"),
               mono=False, dur=3.6, api_name="/do_emblem")
print("徽记 OK:", r2[0].split("\\")[-1], "|", r2[2])
