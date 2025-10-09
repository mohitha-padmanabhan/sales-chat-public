import subprocess, os, sys, uvicorn, fastapi, sse_starlette, json, asyncio
from fastapi import FastAPI, Request, Response
from sse_starlette.sse import EventSourceResponse

app = FastAPI(title="SalesCI-MCP-Proxy")

# spawn your stdio server
proc = subprocess.Popen(
    [sys.executable, "main.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

async def gen(request: Request):
    while True:
        if await request.is_disconnected():
            break
        line = proc.stdout.readline()
        if not line:
            break
        yield dict(data=line)

@app.post("/message")
async def message(req: Request):
    body = await req.body()
    proc.stdin.write(body.decode() + "\n")
    proc.stdin.flush()
    return Response(status_code=200)

@app.get("/sse")
async def sse(req: Request):
    return EventSourceResponse(gen(req))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)