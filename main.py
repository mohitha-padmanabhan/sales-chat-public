import os, pandas as pd, plotly.express as px, base64, io, uuid, textwrap
from fastmcp import FastMCP
from cachetools import TTLCache
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("SalesCI")
cache = TTLCache(maxsize=200, ttl=86_400)

@mcp.tool()
def upload_sales_csv(csv_text: str) -> str:
    sid = str(uuid.uuid4())
    cache[sid] = {"df": pd.read_csv(io.StringIO(csv_text)), "hist": []}
    return sid

@mcp.tool()
def ask_question(session_id: str, question: str) -> dict:
    if session_id not in cache:
        return {"error": "Session not found"}
    df = cache[session_id]["df"]

    sys = "You MUST reply with ONLY valid Python code. Use df, pd, px. End with answer and fig. No comments."
    prompt = f"Columns: {list(df.columns)}\nQuestion: {question}"

    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    resp = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": sys},
                  {"role": "user", "content": prompt}],
        temperature=0
    )
    code = resp.choices[0].message.content

    l = {"df": df, "pd": pd, "px": px, "answer": "", "fig": None}
    try:
        exec(code, {}, l)
    except Exception as e:
        l["answer"] = f"Sorry, I couldn’t build that answer ({e}). Please rephrase."
        l["fig"] = None

    ans = l.get("answer", "")
    fig_b64 = base64.b64encode(l["fig"].to_image(format="png")).decode() if l["fig"] else None
    return {"answer": ans, "fig_b64": fig_b64}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.app, host="0.0.0.0", port=8000, log_level="info")