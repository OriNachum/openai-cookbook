from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sqlite3
import json

# start with: uvicorn main:app --reload --port 8003

app = FastAPI()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.post("/run_query/")
async def run_query(query: str):
    try:
        con = sqlite3.connect("mydatabase.db")
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return JSONResponse(content=json.dumps(rows))
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    finally:
        if con:
            con.close()
