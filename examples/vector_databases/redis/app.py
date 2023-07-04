import redis
from datetime import date
from fastapi import FastAPI, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from scripts.search_redis import search_redis

app = FastAPI()

# Define Pydantic models
class NewRecord(BaseModel):
    question: str
    answer: str
    date: date
    company_name: str
    company_size: str
    company_location: str
    company_industry: str

class UpdateRecord(BaseModel):
    question: str
    vote: int
    vote_reason: Optional[str] = None

class DeleteRecord(BaseModel):
    question: str
    delete_reason: str
    delete_owner: str

# In-memory storage for simplicity. Replace with actual database in production.
records = []

@app.post("/search/")
async def create_record(record: List[NewRecord]):
    # Here, you should implement logic to add a new record to your database
    records.append(record.dict())
    return {"detail": "Record created"}

@app.put("/search/")
async def update_record(record: UpdateRecord):
    # Here, you should implement logic to update an existing record in your database
    for r in records:
        if r['question'] == record.question:
            r['vote'] = record.vote
            r['vote_reason'] = record.vote_reason
            return {"detail": "Record updated"}
    raise HTTPException(status_code=404, detail="Record not found")

@app.delete("/search/")
async def delete_record(record: DeleteRecord):
    # Here, you should implement logic to delete a record from your database
    for r in records:
        if r['question'] == record.question:
            records.remove(r)
            return {"detail": "Record deleted"}
    raise HTTPException(status_code=404, detail="Record not found")

@app.get("/search/{query}")
async def search(query: str):
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    results = search_redis(redis_client, query, vector_field='question_vector', k=3)  # call your search method
    return results
