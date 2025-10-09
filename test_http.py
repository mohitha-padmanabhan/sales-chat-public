import requests, json

URL = "https://sales-chat-public-production.up.railway.app/mcp"
payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
r = requests.post(URL, json=payload, headers={"Accept": "application/json, text/event-stream"})
print("RAW TEXT:", r.text)
print("STATUS:", r.status_code)