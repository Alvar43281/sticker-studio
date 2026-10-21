from gradio_client import Client, handle_file
c = Client("http://127.0.0.1:7870", verbose=False)
r1 = c.predict(img=handle_file(r"D:\agent\poster-studio\src_clean.png"),
               m="贴纸模式", border_name="白色", bpx=10,
               top_t="打工吧", bottom_t="今天也是", eff="果冻", bgc="白",
               mono_c=False, dur_v=3.6, api_name="/dispatch")
print("贴纸:", r1[0].split("\\")[-1] if r1[0] else "None", "|", r1[2])
r2 = c.predict(img=handle_file(r"D:\agent\sequence-evolver\demo_sigil.png"),
               m="徽记模式", border_name="白色", bpx=10,
               top_t="", bottom_t="", eff="冲击", bgc="白",
               mono_c=False, dur_v=3.6, api_name="/dispatch")
print("徽记:", r2[0].split("\\")[-1] if r2[0] else "None", "|", r2[2])
