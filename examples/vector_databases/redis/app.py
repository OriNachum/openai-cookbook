import redis
from datetime import date
from fastapi import FastAPI, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from scripts.do_validate_key import do_validate_key
from scripts.delete_record import delete_record
from scripts.update_record import update_record
from scripts.add_records import add_records
from scripts.search_redis import search_redis
import openai 

from dotenv import dotenv_values

# Load environment variables from .env file
env_vars = dotenv_values('.env')

VALIDATE_KEY_RESULT = do_validate_key(openai)
print(VALIDATE_KEY_RESULT)

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
async def create_records_endpoint(records: List[NewRecord]):
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any
    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    # Here, you should implement logic to add new records to your database
    add_records(redis_client, records)
    return {"detail": "Records created"}

@app.put("/search/")
async def update_record_endpoint(record: UpdateRecord):
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    # Here, you should implement logic to update an existing record in your database
    update_record(redis_client, record.question, record.vote, record.vote_reason)
    return {"detail": "Record updated"}

@app.delete("/search/")
async def delete_record_endpoint(record: DeleteRecord):
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    # Here, you should implement logic to delete a record from your database
    delete_record(redis_client, record.question, record.delete_reason, record.delete_owner)
    return {"detail": "Record deleted"}

@app.get("/search/{query}")
async def search(query: str):
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    results = search_redis(redis_client, query, vector_field='question_vector', k=3)  # call your search method
    return results
