import requests
r = requests.post("http://127.0.0.1:23334/screenshot", timeout=30)
print(r.status_code, r.text)
