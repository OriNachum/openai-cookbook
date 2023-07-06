from fastapi import FastAPI, HTTPException
import pyodbc

app = FastAPI()

# establish the connection
def get_db_connection():
    conn_str = (
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        r'SERVER=your_server;'
        r'DATABASE=your_database;'
        r'UID=your_username;'
        r'PWD=your_password;'
    )
    conn = pyodbc.connect(conn_str)
    return conn

@app.get("/execute")
async def execute_sql(command: str):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(command)
            result = cursor.fetchall()
            return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
