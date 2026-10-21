from gradio_client import Client, handle_file
c = Client("http://127.0.0.1:7870", verbose=False)
r = c.predict(img=handle_file(r"D:\agent\poster-studio\src_clean.png"),
              m="贴纸模式", border_name="白色", bpx=9,
              top_t="打工吧", bottom_t="今天也是", eff="流光", bgc="白",
              mono_c=False, dur_v=3.6, api_name="/dispatch")
print("返回文件:", [p.split("\\")[-1] for p in r[0]])
print("信息:", r[2])
