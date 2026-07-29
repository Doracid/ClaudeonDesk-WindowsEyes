import requests
resp = requests.post("http://127.0.0.1:23334/screenshot", timeout=10)
print(resp.status_code, resp.text)
