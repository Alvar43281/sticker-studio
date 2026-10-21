from gradio_client import Client, handle_file
c = Client("http://127.0.0.1:7870", verbose=False)
info = c.view_api(return_format="dict")
print("端点:", list(info["named_endpoints"].keys()))
r = c.predict(img=handle_file(r"D:\agent\素材\袋鼠.png"), make_white=True, make_black=True, api_name="/do_cutout")
print("抠图输出:", [p.split("\\")[-1] for p in r[1]])
print(r[2])
