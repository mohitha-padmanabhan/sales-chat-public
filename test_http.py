import requests, json

URL = "https://sales-chat-public-production.up.railway.app"
payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
r = requests.post(URL, json=payload)
print("RAW TEXT:", repr(r.text))
print("STATUS:", r.status_code)