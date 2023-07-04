import redis

from scripts.search_redis import search_redis
from dotenv import dotenv_values

# Load environment variables from .env file
env_vars = dotenv_values('.env')

def run_query_loop(redis_client):
    while True:
        user_query = input('Enter your query (or Q to quit): ')
        if user_query.lower() == 'q':
            break
        else:
            results = search_redis(redis_client, user_query, vector_field='question_vector', k=3)
            for i, article in enumerate(results):
                score = 1 - float(article.vector_score)
                print(f"{i}. {article.answer} (Score: {round(score ,3 )}\n")
            print('\n')

if __name__ == "__main__":
    redis_host = "localhost"  # replace with your Redis ",host
    redis_port = 6379         # replace with your Redis port
    redis_password = ""       # replace with your Redis password if any

    redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
    run_query_loop(redis_client)
