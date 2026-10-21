from gradio_client import Client, handle_file
c = Client("http://127.0.0.1:7870", verbose=False)
info = c.view_api(return_format="dict")
print("端点:", list(info["named_endpoints"].keys()))
print("参数:", list(info["named_endpoints"].get("/dispatch", {}).get("parameters", [])))
