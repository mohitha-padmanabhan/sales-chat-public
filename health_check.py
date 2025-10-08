import requests
root = "http://localhost:8000"
for p in ("/mcp", "/mcp/message", "/message", "/sse", "/"):
    print(p, requests.post(root+p, json={}).status_code,
          requests.get(root+p).status_code)