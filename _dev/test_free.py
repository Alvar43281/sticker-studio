from gradio_client import Client, handle_file
c = Client("http://127.0.0.1:7870", verbose=False)
info = c.view_api(return_format="dict")
print("参数:", [p["parameter_name"] for p in info["named_endpoints"]["/do_sticker"]["parameters"]])
# 无动效
r = c.predict(img=handle_file(r"D:\agent\素材\奶龙_开心.png"), border_name="无", bpx=9,
              text="自由定位", tx=50, ty=14, effect="无", bg_name="白", no_cut=False,
              api_name="/do_sticker")
print("无动效 ->", [p.split(chr(92))[-1] for p in r[1]], "|", r[2])
# 位置 20/80
r2 = c.predict(img=handle_file(r"D:\agent\素材\奶龙_开心.png"), border_name="无", bpx=9,
               text="左下角", tx=22, ty=82, effect="弹跳", bg_name="白", no_cut=False,
               api_name="/do_sticker")
print("左下定位 ->", [p.split(chr(92))[-1] for p in r2[1]])
