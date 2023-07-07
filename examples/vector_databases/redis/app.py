import redis
from datetime import date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from scripts.do_validate_key import do_validate_key
from scripts.delete_record import delete_record
from scripts.update_record import update_record
from scripts.add_records import add_records
from scripts.search_redis import search_redis
from scripts.complete_prompt import QueryParams, complete_prompt

import openai 

from dotenv import dotenv_values

# Load environment variables from .env file
env_vars = dotenv_values('.env')

VALIDATE_KEY_RESULT = do_validate_key(openai)
print(VALIDATE_KEY_RESULT)

app = FastAPI()

origins = [
    "http://localhost:3000",    # React
    "http://localhost:8000",    # Vue.js
    "http://localhost:8080",    # Angular
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Pydantic models
class NewRecord(BaseModel):
    question: str
    answer: str
    isWin: bool
    companyName: Optional[str]
    companySize: Optional[str]
    companyIndustry: Optional[str]
    companyCountry: Optional[str]
    conversationDate: date

class UpdateRecord(BaseModel):
    questionId: str
    vote: int
    vote_reason: Optional[str] = None

class DeleteRecord(BaseModel):
    questionId: str
    delete_reason: str
    delete_owner: str

# In-memory storage for simplicity. Replace with actual database in production.
records = []

@app.post("/embedded/index-models")
async def create_records_endpoint(records: List[NewRecord]):
    await create_records_internal(records)
    return {"detail": "Records created"}

@app.post("/embedded/index-model")
async def create_record_endpoint(record: NewRecord):
    records=[record]
    await create_records_internal(records)
    return {"detail": "Record created"}

async def create_records_internal(records: List[NewRecord]):
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any
    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    # Here, you should implement logic to add new records to your database
    add_records(redis_client, records)


@app.put("/embedded/rate-model")
async def update_record_endpoint(record: UpdateRecord):
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    # Here, you should implement logic to update an existing record in your database
    update_record(redis_client, record.questionId, record.vote, record.vote_reason)
    return {"detail": "Record updated"}

@app.delete("/embedded/remove-model")
async def delete_record_endpoint(record: DeleteRecord):
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    # Here, you should implement logic to delete a record from your database
    delete_record(redis_client, record.questionId, record.delete_reason, record.delete_owner)
    return {"detail": "Record deleted"}

@app.get("/questions/{question}")
async def search(question: str):
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    results = search_redis(redis_client, question, vector_field='question_vector', k=3)  # call your search method
    return results

@app.get("/ask/{query}")
async def ask(query: str, params: QueryParams):
    response = complete_prompt(query, params)
    return {"response": response}
