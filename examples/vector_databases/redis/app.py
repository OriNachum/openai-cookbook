from datetime import date
import redis
from fastapi import FastAPI
from scripts.search_redis import search_redis
from pydantic import BaseModel
from typing import List

class Item(BaseModel):
    question: str
    answer: str
    date: date
    quality: int
    qualityreason: str

app = FastAPI()

@app.post("/search")
async def insert(items: List[Item]):
    return "Not implemented yet"

@app.put("/search")
async def update(query: str):
    return "Not implemented yet"

@app.delete("/search")
async def delete(query: str):
    return "Not implemented yet"


@app.get("/search/{query}")
async def search(query: str):
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    results = search_redis(redis_client, query, vector_field='question_vector', k=3)  # call your search method
    return results
