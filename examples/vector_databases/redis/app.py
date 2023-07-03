import redis
from fastapi import FastAPI
from scripts.search_redis import search_redis

app = FastAPI()

# @app.post("/index")
# async def index(item: IndexItem):
#     your_redis_module.index(item.data)  # call your index method
#     return {"message": "Indexed successfully"}

@app.get("/search/{query}")
async def search(query: str):
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

    results = search_redis(redis_client, query, vector_field='question_vector', k=3)  # call your search method
    return results
