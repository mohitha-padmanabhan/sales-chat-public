import subprocess, os, sys, uvicorn, fastapi, sse_starlette, json, asyncio
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

app = FastAPI(title="SalesCI-MCP-Proxy")

# CORS allow all (Inspector needs it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# spawn your stdio server
proc = subprocess.Popen(
    [sys.executable, "main.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

# ---------- root health ----------
@app.get("/")
def health():
    return {"status": "ok"}

# ---------- JSON-RPC entry ----------
@app.post("/message")
async def message(req: Request):
    body = await req.body()
    proc.stdin.write(body.decode() + "\n")
    proc.stdin.flush()
    return Response(content=body, status_code=200)

# ---------- SSE stream ----------
@app.get("/sse")
async def sse(req: Request):
    async def gen():
        while True:
            if await req.is_disconnected():
                break
            line = proc.stdout.readline()
            if not line:
                break
            yield dict(data=line)
    return EventSourceResponse(gen())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)