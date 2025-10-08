import os, pandas as pd, plotly.express as px, base64, io, uuid
from fastmcp import FastMCP
from cachetools import TTLCache
from dotenv import load_dotenv
load_dotenv()
import textwrap

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

    # ---- strict prompt ----
    sys = (
        "You MUST reply with ONLY valid Python code.\n"
        "Use ONLY variables: df, pd, px.\n"
        "End with two variables:\n"
        "    answer = <markdown string>\n"
        "    fig = <plotly figure or None>\n"
        "No comments, no explanation, no back-ticks.\n"
        f"DataFrame columns are exactly: {list(df.columns)}"
    )
    prompt = textwrap.dedent('''
top = df.groupby("Rep")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False).head(5)
ans_rows = []
for i, row in top.iterrows():
    ans_rows.append(f"| {i+1} | {row.Rep} | {row.Revenue} |")
answer = "| Rank | Rep | Revenue |\\n|------|-----|----------|\\n" + "\\n".join(ans_rows)
fig = None
''')

    import openai, os
    openai.api_key = os.getenv("OPENAI_API_KEY")
    resp = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": sys},
                  {"role": "user", "content": prompt}],
        temperature=0
    )
    code = resp.choices[0].message.content

        # ---- safe execute ----
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
   mcp.run(transport="stdio")
